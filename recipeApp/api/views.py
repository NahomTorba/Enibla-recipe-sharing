from django.db.models import Q
from recipeApp.models import Recipe
from userApp.models import UserProfile
from recipeApp.api.serializer import RecipeSerializer, RecipeCreateUpdateSerializer
from rest_framework import viewsets, permissions
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView

from recipeApp.views import TAG_CHOICES, CUISINE_CHOICES

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer
    
    def perform_create(self, serializer):
        # Automatically set the author to the logged-in user's profile
        profile = UserProfile.objects.get(user=self.request.user)
        serializer.save(author=profile)
    
class IsOwner(BasePermission):
    #Custom permission to only allow owners of a recipe to edit it.
    
    def has_object_permission(self, request, view, obj):
        return obj.author.user == request.user


class RecipeCreateUpdateViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Users can only see and modify their own recipes
        profile = UserProfile.objects.get(user=self.request.user)
        return Recipe.objects.filter(author=profile)

    def perform_create(self, serializer):
        profile = UserProfile.objects.get(user=self.request.user)
        serializer.save(author=profile)

    def perform_update(self, serializer):
        profile = UserProfile.objects.get(user=self.request.user)
        serializer.save(author=profile)

    def perform_destroy(self, instance):
        instance.delete()

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj
    
#additional API views 

# API: List all recipes
class RecipeListAPIView(ListAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.AllowAny]

# API: Retrieve a single recipe by slug
class RecipeDetailAPIView(RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

# API: Search recipes by title, ingredients, or tags
class RecipeSearchAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.GET.get('q', '').strip()
        recipes = Recipe.objects.all()
        if query:
            recipes = recipes.filter(
                Q(title__icontains=query) |
                Q(ingredients__icontains=query) |
                Q(tags__icontains=query)
            )
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)

# API: List all available tags
class RecipeTagListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        tags = [tag[0] for tag in TAG_CHOICES]
        return Response(tags)

# API: List all available cuisines
class RecipeCuisineListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cuisines = [cuisine[0] for cuisine in CUISINE_CHOICES]
        return Response(cuisines)
