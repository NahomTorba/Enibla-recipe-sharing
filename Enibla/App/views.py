from django.shortcuts import render,redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm, UserProfileForm, RecipeForm
from .models import UserProfile, Recipe
from .email_utils import send_confirmation_email



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
            if user is not None:
                login(request, user)
                messages.success(request, 'Welcome to Enibla! Please create your profile to get started.')
                return redirect('index')
            else:
                messages.error(request, 'Failed to authenticate user after signup')
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
                messages.success(request, f'Welcome back, {user.first_name if user.first_name else username}!')
                
                # Redirect to the next page if provided, otherwise to profile
                next_page = request.POST.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, 'auth/login.html', {'form': form})
    else:
        form = AuthenticationForm()
        return render(request, 'auth/login.html', {'form': form})

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
    
    # Get trending recipes (top 6 by views)
    trending_recipes = Recipe.objects.all().order_by('-views')[:6]
    
    # Get community stats
    total_recipes = Recipe.objects.count()
    total_users = User.objects.count()
    total_cuisines = len(CUISINE_CHOICES)
    total_favorites = 0  # Placeholder for when favorites are implemented
    
    context = {
        'featured_recipes': featured_recipes,
        'trending_recipes': trending_recipes,
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
            profile = form.save(commit=False)
            profile.user = request.user

            favorite_cuisines = request.POST.getlist('favorite_cuisines')
            profile.favorite_cuisines = ','.join(favorite_cuisines)

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
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        recipes = Recipe.objects.filter(author=profile).order_by('-created_at')
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, 'Profile not found.')
        return redirect('home')
    
    context = {
        'profile': profile,
        'recipes': recipes,
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

@require_http_methods(["GET", "POST"])
@login_required
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

class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 12  # Show 12 recipes per page
    
    def get_queryset(self):
        """Return filtered recipes based on search query"""
        queryset = Recipe.objects.all()
        search_query = self.request.GET.get('q')
        
        if search_query:
            # Search in recipe title, ingredients, and cuisine
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(ingredients__icontains=search_query) |
                Q(cuisine__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_recipes'] = Recipe.objects.count()
        context['search_query'] = self.request.GET.get('q', '')
        return context

def recipe_list_view(request):
    """
    Function-based view alternative for recipe list
    """
    # Get search query from request
    search_query = request.GET.get('q')
    
    # Filter recipes based on search query
    recipes = Recipe.objects.all()
    if search_query:
        recipes = recipes.filter(
            Q(title__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(cuisine__icontains=search_query)
        )
    
    recipes = recipes.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(recipes, 12)  # Show 12 recipes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'recipes': page_obj,
        'total_recipes': recipes.count(),
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'recipes/recipe_list.html', context)

def recipe_detail(request, slug):
    """Display detailed view of a single recipe"""
    recipe = get_object_or_404(Recipe, slug=slug)
    
    # Increment views count
    recipe.increment_views()
    
    # Fetch all reviews for this recipe
    reviews = recipe.reviews.select_related('user__userprofile').all()
    
    # Image url in the view
    image_url = request.build_absolute_uri(recipe.image.url) if recipe.image else None
    
    # Get related recipes (same tags or author)
    related_recipes = Recipe.objects.filter(
        Q(tags__icontains=recipe.tags) | Q(author=recipe.author)
    ).exclude(pk=recipe.pk).distinct()[:4]
    
    context = {
        'recipe': recipe,
        'related_recipes': related_recipes,
        'reviews': reviews,
        'image_url': image_url,
    }
    return render(request, 'recipes/recipe_detail.html', context)

def homepage(request):
    featured_recipes = Recipe.objects.filter(is_featured=True).order_by('-created_at')[:5]
    return render(request, 'homepage.html', {'featured_recipes': featured_recipes})

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.increment_views()  # Increment view count
    
    # Get related recipes by same author
    related_recipes = Recipe.objects.filter(author=recipe.author).exclude(pk=pk)[:4]
    
    context = {
        'recipe': recipe,
        'related_recipes': related_recipes
    }
    return render(request, 'recipe_detail.html', context)
