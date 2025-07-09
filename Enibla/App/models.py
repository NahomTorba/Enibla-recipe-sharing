from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, null=True)
    CUISINE_CHOICES = [
        ('Ethiopian', 'Ethiopian'),
        ('Eritrea', 'Eritrea'),
        ('African', 'African'),
        ('Italian', 'Italian'),
        ('Mexican', 'Mexican'),
        ('Chinese', 'Chinese'),
        ('Japanese', 'Japanese'),
        ('Indian', 'Indian'),
        ('French', 'French'),
        ('American', 'American'),
        ('Korean', 'Korean'),
        ('Spanish', 'Spanish'),
        ('Middle Eastern', 'Middle Eastern'),
        ('Brazilian', 'Brazilian'),
        ('British', 'British'),
    ]
    favorite_cuisines = models.CharField(max_length=200, blank=True)  # fixed: max_length added
    profile_image = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_favorite_cuisines_list(self):
        if self.favorite_cuisines:
            return self.favorite_cuisines.split(',')
        return []

    class Meta:  # Fixed capitalization (must be Meta)
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class Recipe(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    prep_time = models.IntegerField(blank=True, null=True)
    cook_time = models.IntegerField(blank=True, null=True)
    servings = models.IntegerField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    TAG_CHOICES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('dessert', 'Dessert'),
        ('snack', 'Snack'),
        ('fasting', 'Fasting'),
    )
    tags = models.CharField(max_length=100, blank=True)
    image = models.ImageField(
        upload_to='recipe_images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def get_tag_choices_list(self):
        if self.tags:
            return self.tags.split(',')
        return []

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

