from rest_framework import serializers
from recipeApp.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'ingredients', 'instructions', 'created_at', 'updated_at', 'author']
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']

class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 'image', 'cuisine', 'difficulty', 'prep_time']
        read_only_fields = ['author']
    def validate_title(self, value):
        if Recipe.objects.filter(title=value).exists():
            raise serializers.ValidationError("A recipe with this title already exists.")
        return value
    def validate_description(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return value
    def validate_ingredients(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Ingredients must be at least 10 characters long.")
        return value
    def validate_instructions(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Instructions must be at least 10 characters long.")
        return value
    def validate_prep_time(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Preparation time must be a positive integer.")
        return value
    def validate_difficulty(self, value):
        valid_difficulties = [choice[0] for choice in Recipe.DIFFICULTY_CHOICES]
        if value and value not in valid_difficulties:
            raise serializers.ValidationError(f"Difficulty must be one of {valid_difficulties}.")
        return value
    def validate_cuisine(self, value):
        valid_cuisines = [choice[0] for choice in Recipe.CUISINE_CHOICES]
        if value and value not in valid_cuisines:
            raise serializers.ValidationError(f"Cuisine must be one of {valid_cuisines}.")
        return value

