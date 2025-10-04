from django.urls import path, include
from recipeApp.api import views
from rest_framework.routers import DefaultRouter
from recipeApp.api.views import RecipeViewSet, RecipeCreateUpdateViewSet

router = DefaultRouter()
router.register(r'Recipe', RecipeViewSet, basename='recipe')
router.register(r'RecipeCreateUpdate', RecipeCreateUpdateViewSet, basename='recipe_create_update')

urlpatterns = [
     # REST API URLs
    path('api/', include(router.urls)),  # Include the router URLs

    # Additional API endpoints
    path('api/recipes/', views.RecipeListAPIView.as_view(), name='api_recipe_list'),
    path('api/recipes/<slug:slug>/', views.RecipeDetailAPIView.as_view(), name='api_recipe_detail'),
    path('api/recipes/search/', views.RecipeSearchAPIView.as_view(), name='api_recipe_search'),
    path('api/tags/', views.RecipeTagListAPIView.as_view(), name='api_tag_list'),
    path('api/cuisines/', views.RecipeCuisineListAPIView.as_view(), name='api_cuisine_list'),
]