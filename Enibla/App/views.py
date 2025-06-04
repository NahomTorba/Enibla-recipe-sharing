from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .email_utils import send_confirmation_email
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib.auth.models import User
from django.contrib.auth import logout

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
                messages.success(request, f'Welcome back, {user.first_name if user.first_name else username}!')
                
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

@login_required
def index(request):
    html = """
        <html>
            <head>
                <title>Enibla - Home</title>
                <meta charset="UTF-8">
            </head>
            <body>
                <h1>Welcome to Enibla</h1>
                <h2>This is the sample home page this means you have logged in successfully </h2>
            </body>
        </html>
    """
    return HttpResponse(html)

CUISINE_CHOICES = [('Italian', 'Italian'),('Mexican', 'Mexican'),('Chinese', 'Chinese'),('Japanese', 'Japanese'),('Indian', 'Indian'),('French', 'French'),('Thai', 'Thai'),('Mediterranean', 'Mediterranean'),('American', 'American'),('Korean', 'Korean'),('Vietnamese', 'Vietnamese'),('Greek', 'Greek'),('Spanish', 'Spanish'),('Middle Eastern', 'Middle Eastern'),('Brazilian', 'Brazilian'),('German', 'German'),('British', 'British'),('African', 'African'),('Caribbean', 'Caribbean'),('Fusion', 'Fusion'),]

@login_required
def profile_create(request):
# giving a test user until we do registration and authenticated login
    test_user = User.objects.first()
    request.user = test_user
    profile, created = UserProfile.objects.get_or_create(user=request.user)
# test user end here
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
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, 'Profile not found.')
        return redirect('home')
    
    context = {
        'profile': profile,
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
    
TAG_CHOICES = (('breakfast', 'Breakfast'),('lunch', 'Lunch'),('dinner', 'Dinner'),('dessert', 'Dessert'),('snack', 'Snack'),('fasting', 'Fasting'),)

def create_recipe(request):
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
            return redirect('recipe_detail', recipe_id=recipe.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecipeForm()
    
    context = {
        'form': form,
        'tag_choices': TAG_CHOICES,
    }
    return render(request, 'create_recipe.html', context)

