from rest_framework import serializers
from .models import Recipe, Review, SavedRecipe
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'