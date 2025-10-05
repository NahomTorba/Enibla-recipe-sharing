from django.urls import path, include
from recipeApp.api import views
from rest_framework.routers import DefaultRouter
from recipeApp.api.views import RecipeViewSet, RecipeCreateUpdateViewSet

router = DefaultRouter()
router.register(r'Recipe', RecipeViewSet, basename='recipe')
router.register(r'RecipeCreateUpdate', RecipeCreateUpdateViewSet, basename='recipe_create_update')

urlpatterns = [
     # REST API URLs
    path('', include(router.urls)),  # Include the router URLs

    # Additional API endpoints
    path('recipes/', views.RecipeListAPIView.as_view(), name='api_recipe_list'),
    path('recipes/<slug:slug>/', views.RecipeDetailAPIView.as_view(), name='api_recipe_detail'),
    path('recipes/search/', views.RecipeSearchAPIView.as_view(), name='api_recipe_search'),
    path('tags/', views.RecipeTagListAPIView.as_view(), name='api_tag_list'),
    path('cuisines/', views.RecipeCuisineListAPIView.as_view(), name='api_cuisine_list'),
]