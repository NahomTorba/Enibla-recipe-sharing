from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    # sample url for home page
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),

    

    # URLs for recipes
    path('recipes/create/', views.create_recipe, name='create_recipe'),

    # URLs for recipe editing and deletion
    path('recipes/<slug:slug>/edit/', views.edit_recipe, name='edit_recipe'),
    path('recipes/<slug:slug>/delete/', views.delete_recipe, name='delete_recipe'),

    path('recipes/', views.recipe_list_view, name='recipe_list'),

    # URLs for detailed recipe view
    path('recipe/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/<slug:slug>/review/add', views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    # API Endpoints for saved recipes
    path('api/check-saved-recipe/<slug:slug>/', views.check_saved_recipe, name='check_saved_recipe'),
    path('api/save-recipe/<slug:slug>/', views.save_recipe, name='save_recipe'),
    path('api/unsave-recipe/<slug:slug>/', views.unsave_recipe, name='unsave_recipe'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
