from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('profile/create/', views.profile_create, name='create_profile'),
]
