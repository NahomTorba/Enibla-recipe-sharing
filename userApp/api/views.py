from django.contrib.auth import authenticate
from userApp.models import UserProfile
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from userApp.api.serializer import (
    UserSerializer, UserProfileSerializer, UserCreateSerializer, 
    UserProfileCreateUpdateSerializer
)
from django.contrib.auth.models import User
from django.contrib.auth import authenticate




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
    