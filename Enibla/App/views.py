from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib.auth.models import User

# Create your views here.
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
    return render(request, 'Create_Profile.html', context)

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
    return render(request, 'profile_detail.html', context)

def my_profile(request):
    """Redirect to current user's profile"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        return redirect('profile_detail', username=request.user.username)
    except UserProfile.DoesNotExist:
        return redirect('create_profile')
