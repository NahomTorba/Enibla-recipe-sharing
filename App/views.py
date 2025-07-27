from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .forms import SignUpForm, UserProfileForm, RecipeForm
from .models import UserProfile, Recipe
from .email_utils import send_confirmation_email

# constants
CUISINE_CHOICES = [
    ('Ethiopian', 'Ethiopian'),
    ('Eritrea', 'Eritrea'),
    ('African', 'African'),
    ('Italian', 'Italian'),
    ('Mexican', 'Mexican'),
    ('Chinese', 'Chinese'),
    ('Japanese', 'Japanese'),
    ('Indian', 'Indian'),
    ('French', 'French'),
    ('American', 'American'),
    ('Korean', 'Korean'),
    ('Spanish', 'Spanish'),
    ('Middle Eastern', 'Middle Eastern'),
    ('Brazilian', 'Brazilian'),
    ('British', 'British'),
]
TAG_CHOICES = [
    ('breakfast', 'Breakfast'),
    ('lunch', 'Lunch'),
    ('dinner', 'Dinner'),
    ('dessert', 'Dessert'),
    ('snack', 'Snack'),
    ('fasting', 'Fasting'),
]

def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_confirmation_email(user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            
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
    
    context = {'form': form}
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
    featured_recipes = Recipe.objects.select_related('author__user').order_by('-created_at')[:6]
    trending_recipes = Recipe.objects.all().order_by('-views')[:6]
    
    context = {
        'featured_recipes': featured_recipes,
        'trending_recipes': trending_recipes,
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
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'cuisines': CUISINE_CHOICES,
    }
    return render(request, 'profile/Create_Profile.html', context)

def profile_detail(request, username):
    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        recipes = Recipe.objects.filter(author=profile).order_by('-created_at')
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, 'Profile not found.')
        return redirect('index')
    
    context = {
        'profile': profile,
        'recipes': recipes,
    }
    return render(request, 'profile/profile_detail.html', context)

@login_required
def edit_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('create_profile')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            favorite_cuisines = request.POST.getlist('favorite_cuisines')
            profile.favorite_cuisines = ','.join(favorite_cuisines)
            if request.POST.get('remove_image'):
                profile.profile_image.delete()
                profile.profile_image = None
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_detail', username=request.user.username)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)
    
    selected_cuisines = profile.get_favorite_cuisines_list()
    context = {
        'form': form,
        'cuisines': CUISINE_CHOICES,
        'selected_cuisines': selected_cuisines,
    }
    return render(request, 'profile/edit_profile.html', context)

@login_required
def create_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user.userprofile
            tags = request.POST.getlist('tags')
            recipe.tags = ','.join(tags)
            recipe.save()
            messages.success(request, 'Recipe created successfully!')
            return redirect('recipe_detail', pk=recipe.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecipeForm()
    
    context = {
        'form': form,
        'tags': TAG_CHOICES,
    }
    return render(request, 'recipes/create_recipe.html', context)

class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 12

    def get_queryset(self):
        return Recipe.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_recipes'] = Recipe.objects.count()
        return context

def recipe_list_view(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    paginator = Paginator(recipes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'recipes': page_obj,
        'total_recipes': Recipe.objects.count(),
    }
    return render(request, 'recipes/recipe_list.html', context)

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.increment_views()
    related_recipes = Recipe.objects.filter(author=recipe.author).exclude(pk=pk)[:4]
    
    context = {
        'recipe': recipe,
        'related_recipes': related_recipes
    }
    return render(request, 'recipe_detail.html', context)
