from django.contrib import admin
from .models import UserProfile, Recipe

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'tags')

