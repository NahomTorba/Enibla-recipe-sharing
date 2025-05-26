from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm

# Create your views here.
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
            messages.error(request, 'Please correct the erros!')
    else:
        form = UserProfileForm()
    
    context ={
        'form': form,
        'cuisines': UserProfile.CUISINE_CHOICES,
    }
    return render(request, 'Create_Profile.html', context)