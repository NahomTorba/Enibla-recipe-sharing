from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from recipeApp.models import Recipe
from reviewApp.models import Review, SavedRecipe
from reviewApp.forms import ReviewForm
from reviewApp.api.serializer import ReviewSerializer, SavedRecipeSerializer, ReviewCreateUpdateSerializer
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

@login_required
@require_POST
def add_review(request, slug):
    """Add or update a review for a recipe"""
    recipe = get_object_or_404(Recipe, slug=slug)

    # Check if user already reviewed this recipe
    existing_review = Review.objects.filter(
        user=request.user, 
        recipe=recipe
    ).first()
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        if existing_review:
            # Update existing review with form data
            existing_review.rating = form.cleaned_data['rating']
            existing_review.comment = form.cleaned_data['comment']
            existing_review.save()
            messages.success(request, 'Your review has been updated!')
        else:
            # Create new review
            review = form.save(commit=False)
            review.user = request.user
            review.recipe = recipe
            review.save()
            messages.success(request, 'Your review has been added!')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")

    # Clear the editing session variable if it exists
    if 'editing_review_id' in request.session:
        del request.session['editing_review_id']
        
    return redirect('recipe_detail', slug=slug)

# edit review function
@login_required
def edit_review(request, review_id):
    """Prepare to edit a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    recipe = review.recipe
    
    # We'll set a session variable to indicate edit mode
    request.session['editing_review_id'] = review_id
    
    messages.info(request, 'You can now update your review below.')
    return redirect('recipe_detail', slug=recipe.slug)

# delete review function
@login_required
def delete_review(request, review_id):
    """Delete a review from a recipe using review_id"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    recipe = review.recipe

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted!')
        return redirect('recipe_detail', slug=recipe.slug)
    
    messages.error(request, 'You can only delete your own reviews.')
    return redirect('recipe_detail', slug=recipe.slug)

@login_required
@require_http_methods(["POST"])
def save_recipe(request, slug):
    """Save or unsave a recipe for the user"""
    recipe = get_object_or_404(Recipe, slug=slug)
    saved_recipe, created = SavedRecipe.objects.get_or_create(
        user=request.user,
        recipe=recipe
    )
    
    if not created:
        saved_recipe.delete()
        return JsonResponse({
            'success': True,
            'saved': False,
            'message': 'Recipe removed from saved recipes.'
        })
    else:
        return JsonResponse({
            'success': True,
            'saved': True,
            'message': 'Recipe saved!'
        })

@login_required
def check_saved_recipe(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    is_saved = SavedRecipe.objects.filter(user=request.user, recipe=recipe).exists()
    return JsonResponse({'is_saved': is_saved})

@login_required
@require_http_methods(["POST"])
def unsave_recipe(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    try:
        SavedRecipe.objects.get(user=request.user, recipe=recipe).delete()
        return JsonResponse({'success': True, 'message': 'Recipe unsaved successfully.'})
    except SavedRecipe.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Recipe not found in saved recipes.'})
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
    
