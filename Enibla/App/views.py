from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .email_utils import send_confirmation_email

# Create your views here.
def signup(request):
    if request.user.is_authenticated:
        return redirect('my_profile')
    
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
                return redirect('create_profile')
            else:
                return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    
    context = {
        'form': form,
    }
    return render(request, 'signup.html', context)
