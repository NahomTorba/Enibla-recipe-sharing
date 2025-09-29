from django.urls import path, include
from recipeApp import views
from rest_framework.routers import DefaultRouter
from recipeApp.views import RecipeViewSet, RecipeCreateUpdateViewSet

router = DefaultRouter()
router.register(r'Recipe', RecipeViewSet, basename='recipe')
router.register(r'RecipeCreateUpdate', RecipeCreateUpdateViewSet, basename='recipe_create_update')

urlpatterns = [
    # URLs for recipes
    path('recipes/create/', views.create_recipe, name='create_recipe'),

    # URLs for recipe editing and deletion
    path('recipes/<slug:slug>/edit/', views.edit_recipe, name='edit_recipe'),
    path('recipes/<slug:slug>/delete/', views.delete_recipe, name='delete_recipe'),

    path('recipes/', views.recipe_list_view, name='recipe_list'),

    # URLs for detailed recipe view
    path('recipe/<slug:slug>/', views.recipe_detail, name='recipe_detail'),


    # REST API URLs
    path('api/', include(router.urls)),  # Include the router URLs

    # Additional API endpoints
    path('api/recipes/', views.RecipeListAPIView.as_view(), name='api_recipe_list'),
    path('api/recipes/<slug:slug>/', views.RecipeDetailAPIView.as_view(), name='api_recipe_detail'),
    path('api/recipes/search/', views.RecipeSearchAPIView.as_view(), name='api_recipe_search'),
    path('api/tags/', views.RecipeTagListAPIView.as_view(), name='api_tag_list'),
    path('api/cuisines/', views.RecipeCuisineListAPIView.as_view(), name='api_cuisine_list'),
]