from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from App.models import Recipe,Review,SavedRecipe
from .forms import  RecipeForm, ReviewForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import  Q
from django.core.paginator import Paginator
from userApp.models import UserProfile


# constants
CUISINE_CHOICES = [ ('Ethiopian', 'Ethiopian'), ('Eritrea', 'Eritrea'), ('African', 'African'), ('Italian', 'Italian'),('Mexican', 'Mexican'),('Chinese', 'Chinese'),('Japanese', 'Japanese'),('Indian', 'Indian'),('French', 'French'),('American', 'American'),('Korean', 'Korean'),('Spanish', 'Spanish'),('Middle Eastern', 'Middle Eastern'),('Brazilian', 'Brazilian'),('British', 'British')]
TAG_CHOICES = (('breakfast', 'Breakfast'),('lunch', 'Lunch'),('dinner', 'Dinner'),('dessert', 'Dessert'),('snack', 'Snack'),('fasting', 'Fasting'),)


# Create your views here.

def index(request):
    """Home page view with featured recipes and stats"""
    # Get featured recipes (latest 6)
    featured_recipes = Recipe.objects.select_related('author__user').order_by('-created_at')[:6]
    
    # Get community stats
    total_recipes = Recipe.objects.count()
    total_users = User.objects.count()
    total_cuisines = len(CUISINE_CHOICES)
    total_favorites = 0  # Placeholder for when favorites are implemented
    
    context = {
        'featured_recipes': featured_recipes,
        'total_recipes': total_recipes,
        'total_users': total_users,
        'total_cuisines': total_cuisines,
        'total_favorites': total_favorites,
    }
    return render(request, 'home.html', context)



@login_required
@require_POST
def add_review(request, slug):
    """Add or update a review for a recipe"""
    recipe = get_object_or_404(Recipe, slug=slug)

    # Check if user already reviewed this recipe
    existing_review = Review.objects.filter(
        user=request.user, 
        recipe=recipe
    ).first()
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        if existing_review:
            # Update existing review with form data
            existing_review.rating = form.cleaned_data['rating']
            existing_review.comment = form.cleaned_data['comment']
            existing_review.save()
            messages.success(request, 'Your review has been updated!')
        else:
            # Create new review
            review = form.save(commit=False)
            review.user = request.user
            review.recipe = recipe
            review.save()
            messages.success(request, 'Your review has been added!')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")

    # Clear the editing session variable if it exists
    if 'editing_review_id' in request.session:
        del request.session['editing_review_id']
        
    return redirect('recipe_detail', slug=slug)

# edit review function
@login_required
def edit_review(request, review_id):
    """Prepare to edit a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    recipe = review.recipe
    
    # We'll set a session variable to indicate edit mode
    request.session['editing_review_id'] = review_id
    
    messages.info(request, 'You can now update your review below.')
    return redirect('recipe_detail', slug=recipe.slug)

# delete review function
@login_required
def delete_review(request, review_id):
    """Delete a review from a recipe using review_id"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    recipe = review.recipe

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted!')
        return redirect('recipe_detail', slug=recipe.slug)
    
    messages.error(request, 'You can only delete your own reviews.')
    return redirect('recipe_detail', slug=recipe.slug)

@login_required
@require_http_methods(["POST"])
def save_recipe(request, slug):
    """Save or unsave a recipe for the user"""
    recipe = get_object_or_404(Recipe, slug=slug)
    saved_recipe, created = SavedRecipe.objects.get_or_create(
        user=request.user,
        recipe=recipe
    )
    
    if not created:
        saved_recipe.delete()
        return JsonResponse({
            'success': True,
            'saved': False,
            'message': 'Recipe removed from saved recipes.'
        })
    else:
        return JsonResponse({
            'success': True,
            'saved': True,
            'message': 'Recipe saved!'
        })

@login_required
def check_saved_recipe(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    is_saved = SavedRecipe.objects.filter(user=request.user, recipe=recipe).exists()
    return JsonResponse({'is_saved': is_saved})

@login_required
@require_http_methods(["POST"])
def unsave_recipe(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    try:
        SavedRecipe.objects.get(user=request.user, recipe=recipe).delete()
        return JsonResponse({'success': True, 'message': 'Recipe unsaved successfully.'})
    except SavedRecipe.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Recipe not found in saved recipes.'})

def recipe_list_view(request):
    """
    Function-based view for recipe list with backend filtering
    """
    recipes = Recipe.objects.all().order_by('-created_at')

    # Get search query and tag filter from GET params
    query = request.GET.get('q', '').strip()
    tag = request.GET.get('tag', '').strip()
    cuisine = request.GET.get('cuisine', '').strip()
    difficulty = request.GET.get('difficulty', '').strip()
    prep_time = request.GET.get('prep_time', '').strip()

    # Filter by search query (title, ingredients, tags)
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(ingredients__icontains=query) |
            Q(tags__icontains=query)
        )

    # Filter by tag
    if tag:
        recipes = recipes.filter(tags__icontains=tag)

    # Filter by cuisine
    if cuisine:
        recipes = recipes.filter(cuisine=cuisine)

    # Filter by difficulty
    if difficulty:
        recipes = recipes.filter(difficulty=difficulty)

    # Filter by prep_time (less than or equal to user input)
    if prep_time.isdigit():
        recipes = recipes.filter(prep_time__lte=int(prep_time))

    # Pagination
    paginator = Paginator(recipes, 12)  # Show 12 recipes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'recipes': page_obj,
        'total_recipes': recipes.count(),
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': query,
        'active_tag': tag,
        'selected_cuisine': cuisine,
        'selected_difficulty': difficulty,
        'selected_prep_time': prep_time,
        'CUISINE_CHOICES': Recipe.CUISINE_CHOICES,
        'DIFFICULTY_CHOICES': Recipe.DIFFICULTY_CHOICES,
    }

    return render(request, 'recipes/recipe_list.html', context)
