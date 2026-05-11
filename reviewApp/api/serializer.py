from rest_framework import serializers
from recipeApp.models import Recipe
from reviewApp.models import  Review, SavedRecipe

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['recipe', 'user', 'rating', 'comment']
        read_only_fields = ['created_at']

class RecipeMiniSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'image', 'slug']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
class SavedRecipeSerializer(serializers.ModelSerializer):
    recipe = RecipeMiniSerializer(read_only=True) 
    class Meta:
        model = SavedRecipe
        fields = ['user', 'recipe']
        read_only_fields = ['saved_at']
class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        read_only_fields = ['user', 'recipe', 'created_at', 'updated_at']