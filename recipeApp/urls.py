from django.urls import path
from recipeApp import views

urlpatterns = [
    # URLs for recipes
    path('create/', views.create_recipe, name='create_recipe'),

    # URLs for recipe editing and deletion
    path('<slug:slug>/edit/', views.edit_recipe, name='edit_recipe'),
    path('<slug:slug>/delete/', views.delete_recipe, name='delete_recipe'),

    path('recipes/', views.recipe_list_view, name='recipe_list'),

    # URLs for detailed recipe view
    path('<slug:slug>/', views.recipe_detail, name='recipe_detail'),


]