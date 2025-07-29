from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from .forms import SignUpForm, ReviewForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .email_utils import send_confirmation_email
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Recipe,Review,SavedRecipe
from .forms import UserProfileForm, RecipeForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import  Q
from django.core.paginator import Paginator


# constants
CUISINE_CHOICES = [ ('Ethiopian', 'Ethiopian'), ('Eritrea', 'Eritrea'), ('African', 'African'), ('Italian', 'Italian'),('Mexican', 'Mexican'),('Chinese', 'Chinese'),('Japanese', 'Japanese'),('Indian', 'Indian'),('French', 'French'),('American', 'American'),('Korean', 'Korean'),('Spanish', 'Spanish'),('Middle Eastern', 'Middle Eastern'),('Brazilian', 'Brazilian'),('British', 'British')]
TAG_CHOICES = (('breakfast', 'Breakfast'),('lunch', 'Lunch'),('dinner', 'Dinner'),('dessert', 'Dessert'),('snack', 'Snack'),('fasting', 'Fasting'),)


# Create your views here.
def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Send confirmation email
            send_confirmation_email(user)
            # Display success message
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            
            # Automatically log in the user
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user:
                login(request, user)
                messages.success(request, 'Welcome to Enibla! Please create your profile to get started.')
                return redirect('index')
            else:
                return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    
    context = {
        'form': form,
    }
    return render(request, 'auth/signup.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Redirect to the next page if provided, otherwise to profile
                next_page = request.POST.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'auth/login.html', context)

@login_required
def logout_view(request):
    user_name = request.user.first_name if request.user.first_name else request.user.username
    logout(request)
    messages.success(request, f'Goodbye {user_name}! You have been logged out successfully.')
    return redirect('login')

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
def profile_create(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()

            favorite_cuisines = request.POST.getlist('favorite_cuisines')
            profile.favorite_cuisines = ','.join(favorite_cuisines) if favorite_cuisines else ''

            profile.save()
            messages.success(request, 'Profile created successfully!')
            return redirect('profile_detail', username=request.user.username)
        else:
            messages.error(request, 'Please correct the errors!')
    else:
        # Pass the existing profile to the form here as well!
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'cuisines': UserProfile.CUISINE_CHOICES,
    }
    return render(request, 'profile/Create_Profile.html', context)

def profile_detail(request, username):
    try:
        profile = UserProfile.objects.select_related('user').get(user__username=username)
        recipes = Recipe.objects.filter(author=profile).order_by('-created_at')
    except (UserProfile.DoesNotExist):
        messages.error(request, 'Profile not found.')
        return redirect('home')

    saved_recipes = []
    if request.user.is_authenticated and request.user == profile.user:
        saved_recipes = Recipe.objects.filter(savedrecipe__user=request.user)

    context = {
        'profile': profile,
        'recipes': recipes,
        'saved_recipes': saved_recipes,
    }
    return render(request, 'profile/profile_detail.html', context)

def my_profile(request):
    """Redirect to current user's profile"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        return redirect('profile_detail', username=request.user.username)
    except UserProfile.DoesNotExist:
        return redirect('create_profile')
    
def edit_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('create_profile')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Handle favorite cuisines
            favorite_cuisines = request.POST.getlist('favorite_cuisines')
            profile.favorite_cuisines = ','.join(favorite_cuisines)
            
            # Handle image removal
            if request.POST.get('remove_image'):
                profile.profile_image.delete()
                profile.profile_image = None
            
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_detail', username=request.user.username)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Create form with initial data
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'username': request.user.username,
            'email': request.user.email,
        }
        form = UserProfileForm(instance=profile, initial=initial_data)
    
    # Pre-populate favorite cuisines
    if profile.favorite_cuisines:
        selected_cuisines = [cuisine.strip() for cuisine in profile.favorite_cuisines.split(',') if cuisine.strip()]
    else:
        selected_cuisines = []
    
    context = {
        'form': form,
        'profile': profile,
        'cuisines': CUISINE_CHOICES,
        'selected_cuisines': selected_cuisines,
    }
    return render(request, 'profile/edit_profile.html', context)
    

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
