from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib.auth.models import User

# Create your views here.

CUISINE_CHOICES = [('Italian', 'Italian'),('Mexican', 'Mexican'),('Chinese', 'Chinese'),('Japanese', 'Japanese'),('Indian', 'Indian'),('French', 'French'),('Thai', 'Thai'),('Mediterranean', 'Mediterranean'),('American', 'American'),('Korean', 'Korean'),('Vietnamese', 'Vietnamese'),('Greek', 'Greek'),('Spanish', 'Spanish'),('Middle Eastern', 'Middle Eastern'),('Brazilian', 'Brazilian'),('German', 'German'),('British', 'British'),('African', 'African'),('Caribbean', 'Caribbean'),('Fusion', 'Fusion'),]

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
