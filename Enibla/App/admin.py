from django.contrib import admin
from .models import Recipe

# Check if Recipe is already registered
if not any(isinstance(model_admin, admin.ModelAdmin) and model_admin.model == Recipe
        for model_admin in admin.site._registry.values()):
    class RecipeAdmin(admin.ModelAdmin):
        list_display = ('title', 'is_featured', 'views', 'created_at')
        list_filter = ('is_featured',)

    admin.site.register(Recipe, RecipeAdmin)



