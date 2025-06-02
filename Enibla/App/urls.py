from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings


urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
]