from django.shortcuts import get_object_or_404
from reviewApp.models import Review, SavedRecipe
from recipeApp.models import Recipe
from reviewApp.api.serializer import ReviewSerializer, SavedRecipeSerializer, ReviewCreateUpdateSerializer
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReviewCreateUpdateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        recipe_slug = self.request.query_params.get('recipe_slug')
        if recipe_slug:
            queryset = queryset.filter(recipe__slug=recipe_slug)
        return queryset
class SavedRecipeViewSet(viewsets.ModelViewSet):
    serializer_class = SavedRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedRecipe.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
class UserSavedRecipesAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        saved_recipes = SavedRecipe.objects.filter(user=request.user)
        serializer = SavedRecipeSerializer(saved_recipes, many=True)
        return Response(serializer.data)
class RecipeReviewsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        recipe = get_object_or_404(Recipe, slug=slug)
        reviews = Review.objects.filter(recipe=recipe)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
class UserReviewsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reviews = Review.objects.filter(user=request.user)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
