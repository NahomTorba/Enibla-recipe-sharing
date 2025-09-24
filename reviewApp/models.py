from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from App.models import Recipe


# Create your models here.

class Review(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.recipe.title} ({self.rating}/5)"
    
    class Meta:
        unique_together = ['recipe', 'user']
        ordering = ['-created_at']

class SavedRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} saved {self.recipe.title}"
    
    class Meta:
        unique_together = ['user', 'recipe']
        ordering = ['-saved_at']
        
