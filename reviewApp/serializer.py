from rest_framework import serializers
from reviewApp.models import  Review, SavedRecipe

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['recipe', 'user', 'rating', 'comment']
        read_only_fields = ['created_at']

class SavedRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedRecipe
        fields = ['user', 'recipe']
        read_only_fields = ['saved_at']