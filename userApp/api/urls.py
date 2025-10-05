from django.urls import include, path
from rest_framework.routers import DefaultRouter
from userApp.api.views import (
    UserViewSet, UserProfileViewSet, api_register, api_login, 
    api_logout, api_user_profile, api_create_update_profile
)

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    # REST API URLs
    path('', include(router.urls)),  # Include the router URLs
    
    # Additional API endpoints
    path('auth/register/', api_register, name='api_register'),
    path('auth/login/', api_login, name='api_login'),
    path('auth/logout/', api_logout, name='api_logout'),
    path('profile/', api_user_profile, name='api_user_profile'),
    path('profile/create-update/', api_create_update_profile, name='api_create_update_profile'),
]