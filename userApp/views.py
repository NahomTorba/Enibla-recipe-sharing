from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .email_utils import send_confirmation_email
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from userApp.models import UserProfile
from recipeApp.models import Recipe
from userApp.forms import SignUpForm, UserProfileForm
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from userApp.serializer import (
    UserSerializer, UserProfileSerializer, UserCreateSerializer, 
    UserProfileCreateUpdateSerializer
)
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Create your views here.

# constants
CUISINE_CHOICES = [ ('Ethiopian', 'Ethiopian'), ('Eritrea', 'Eritrea'), ('African', 'African'), ('Italian', 'Italian'),('Mexican', 'Mexican'),('Chinese', 'Chinese'),('Japanese', 'Japanese'),('Indian', 'Indian'),('French', 'French'),('American', 'American'),('Korean', 'Korean'),('Spanish', 'Spanish'),('Middle Eastern', 'Middle Eastern'),('Brazilian', 'Brazilian'),('British', 'British')]
TAG_CHOICES = (('breakfast', 'Breakfast'),('lunch', 'Lunch'),('dinner', 'Dinner'),('dessert', 'Dessert'),('snack', 'Snack'),('fasting', 'Fasting'),)


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
    
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model with proper permissions"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user's information"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_me(self, request):
        """Update current user's information"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model with proper permissions"""
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserProfileCreateUpdateSerializer
        return UserProfileSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Create profile for the authenticated user"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Update profile for the authenticated user"""
        if serializer.instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only update your own profile")
        serializer.save()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_profile(self, request):
        """Get current user's profile"""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def create_or_update_my_profile(self, request):
        """Create or update current user's profile"""
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileCreateUpdateSerializer(
                profile, data=request.data, partial=True
            )
        except UserProfile.DoesNotExist:
            serializer = UserProfileCreateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            if hasattr(serializer, 'instance') and serializer.instance:
                serializer.save()
            else:
                serializer.save(user=request.user)
            return Response(UserProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Additional API Views
@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """API endpoint for user registration"""
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """API endpoint for user login"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """API endpoint for user logout"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})
    except:
        return Response({'message': 'Successfully logged out'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_profile(request):
    """API endpoint to get current user's profile"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Profile not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_create_update_profile(request):
    """API endpoint to create or update user profile"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileCreateUpdateSerializer(
            profile, data=request.data, partial=True
        )
    except UserProfile.DoesNotExist:
        serializer = UserProfileCreateUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        if hasattr(serializer, 'instance') and serializer.instance:
            profile = serializer.save()
        else:
            profile = serializer.save(user=request.user)
        
        response_serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    