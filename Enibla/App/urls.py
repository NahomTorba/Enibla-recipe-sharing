from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # URLs for profile
    path('profile/create/', views.profile_create, name='create_profile'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),

    # URLs for recipes
    path('recipes/create/', views.create_recipe, name='create_recipe'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
