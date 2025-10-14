from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from recipeApp.models import Recipe
from recipeApp.forms import RecipeForm
from reviewApp.models import Review, SavedRecipe
from reviewApp.forms import ReviewForm
from userApp.models import UserProfile


# Create your views here.

# constants
CUISINE_CHOICES = [ ('Ethiopian', 'Ethiopian'), ('Eritrea', 'Eritrea'), ('African', 'African'), ('Italian', 'Italian'),('Mexican', 'Mexican'),('Chinese', 'Chinese'),('Japanese', 'Japanese'),('Indian', 'Indian'),('French', 'French'),('American', 'American'),('Korean', 'Korean'),('Spanish', 'Spanish'),('Middle Eastern', 'Middle Eastern'),('Brazilian', 'Brazilian'),('British', 'British')]
TAG_CHOICES = (('breakfast', 'Breakfast'),('lunch', 'Lunch'),('dinner', 'Dinner'),('dessert', 'Dessert'),('snack', 'Snack'),('fasting', 'Fasting'),)

   
@login_required
@require_http_methods(["GET", "POST"])
def create_recipe(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to create recipes.')
        return redirect('login')
    
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please create your profile first before sharing recipes.')
        return redirect('create_profile')
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = profile
            
            # Handle tags
            selected_tags = request.POST.getlist('tags')
            recipe.tags = ','.join(selected_tags)
            
            recipe.save()
            messages.success(request, 'Recipe shared successfully!')
            return redirect('recipe_detail', slug=recipe.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecipeForm()
    
    context = {
        'form': form,
        'tag_choices': TAG_CHOICES,
    }
    return render(request, 'recipes/create_recipe.html', context)

@login_required
def edit_recipe(request, slug):
    try:
        recipe = Recipe.objects.get(slug=slug)
        
        # Check if user owns the recipe
        if recipe.author.user != request.user:
            messages.error(request, "You don't have permission to edit this recipe.")
            return redirect('recipe_detail', slug=slug)

        if request.method == 'POST':
            form = RecipeForm(request.POST, request.FILES, instance=recipe)
            if form.is_valid():
                recipe = form.save(commit=False)
                recipe.author = UserProfile.objects.get(user=request.user)
                
                # Handle tags
                selected_tags = request.POST.getlist('tags')
                recipe.tags = ','.join(selected_tags)
                
                recipe.save()
                messages.success(request, 'Recipe updated successfully!')
                return redirect('recipe_detail', slug=recipe.slug)
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = RecipeForm(instance=recipe)
            # split the stored tags into a list for the form
            recipe_tags = recipe.tags.split(',') if recipe.tags else []

        context = {
            'recipe': recipe,
            'form': form,
            'all_tags': TAG_CHOICES,
            'recipe_tags': recipe_tags,
        }
        return render(request, 'recipes/edit_recipe.html', context)

    except Recipe.DoesNotExist:
        messages.error(request, 'Recipe not found.')
        return redirect('index')


@login_required
def delete_recipe(request, slug):
    try:
        recipe = Recipe.objects.get(slug=slug)
        if recipe.author.user != request.user:
            messages.error(request, 'You can only delete your own recipes.')
            return redirect('recipe_detail', slug=slug)
        
        if request.method == 'POST':
            recipe.delete()
            messages.success(request, 'Recipe has been deleted successfully.')
            return redirect('index')
        
        return render(request, 'recipe_detail.html', {'recipe': recipe})
    except Recipe.DoesNotExist:
        messages.error(request, 'Recipe not found.')
        return redirect('index')
    

def recipe_detail(request, slug):
    """Display detailed view of a single recipe"""
    recipe = get_object_or_404(Recipe, slug=slug)

    # Fetch all reviews for this recipe
    reviews = recipe.reviews.select_related('user__userprofile').all()
    
    # Image url in the view
    image_url = request.build_absolute_uri(recipe.image.url) if recipe.image else None
    
    # Get related recipes (same tags or author)
    related_recipes = Recipe.objects.filter(
        Q(tags__icontains=recipe.tags) | Q(author=recipe.author)
    ).exclude(pk=recipe.pk).distinct()[:4]
    
    # Check if user has saved this recipe
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedRecipe.objects.filter(
            user=request.user, 
            recipe=recipe
        ).exists()

    # User review and editing state
    user_review = None
    has_reviewed = False
    is_editing = False
    
    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, recipe=recipe).first()
        has_reviewed = user_review is not None
        
        # Check if user is in edit mode
        editing_review_id = request.session.get('editing_review_id')
        is_editing = editing_review_id is not None and user_review and str(user_review.id) == str(editing_review_id)
        
        # If we just finished editing, clear the session
        if not is_editing and editing_review_id:
            del request.session['editing_review_id']

    # Initialize review form with proper data if editing
    initial_data = {}
    if user_review and is_editing:
        initial_data = {
            'rating': user_review.rating,
            'comment': user_review.comment
        }
    review_form = ReviewForm(initial=initial_data)

    # Prepare context for rendering the template
    context = {
        'recipe': recipe,
        'related_recipes': related_recipes,
        'is_saved': is_saved,
        'reviews': reviews,
        'has_reviewed': has_reviewed,
        'user_review': user_review,
        'total_reviews': reviews.count(),
        'is_editing': is_editing,
        'review_form': review_form,
        'tag_choices': TAG_CHOICES,
        'cuisine_choices': CUISINE_CHOICES,
        'average_rating': recipe.average_rating,
        'image_url': image_url,
    }
    
    return render(request, 'recipes/recipe_detail.html', context)

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

