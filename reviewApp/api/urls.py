from django.urls import path, include
from reviewApp.api import views
from rest_framework.routers import DefaultRouter
from reviewApp.api.views import SavedRecipeViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'saved-recipes', SavedRecipeViewSet, basename='savedrecipe')
router.register(r'reviews', ReviewViewSet, basename='review')


urlpatterns = [
    # REST API URLs
    path('', include(router.urls)),  # Include the router URLs

    # Additional API endpoints (custom list views)
    path('user/saved-recipes/', views.UserSavedRecipesAPIView.as_view(), name='api_user_saved_recipe_list'),
    path('recipe/<slug:slug>/reviews/', views.RecipeReviewsAPIView.as_view(), name='api_recipe_reviews'),
    path('user/reviews/', views.UserReviewsAPIView.as_view(), name='api_user_reviews'),
]