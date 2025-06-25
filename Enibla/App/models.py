from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator,MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, null=True)
    CUISINE_CHOICES = [ ('Ethiopian', 'Ethiopian'), ('Eritrea', 'Eritrea'), ('African', 'African'), ('Italian', 'Italian'),('Mexican', 'Mexican'),('Chinese', 'Chinese'),('Japanese', 'Japanese'),('Indian', 'Indian'),('French', 'French'),('American', 'American'),('Korean', 'Korean'),('Spanish', 'Spanish'),('Middle Eastern', 'Middle Eastern'),('Brazilian', 'Brazilian'),('British', 'British')]
    favorite_cuisines = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_favorite_cuisines_list(self):
        if self.favorite_cuisines:
            return self.favorite_cuisines.split(',')
        return []
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

class Recipe(models.Model):
    author = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()

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

    def save(self, *args, **kwargs):
        # Auto-generate slug only if it’s missing
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Recipe.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug

        # Update timestamp
        self.updated_at = timezone.now()

        super().save(*args, **kwargs)

        # Resize image if needed
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800))
                img.save(self.image.path)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipe_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('recipe_update', kwargs={'slug': self.slug})

    def get_tag_choices_list(self):
        if not self.tags:
            return []
        tag_list = []
        for tag in self.tags.split(','):
            tag = tag.strip()
            for value, display in self.TAG_CHOICES:
                if value == tag:
                    tag_list.append(display)
                    break
        return tag_list

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum([review.rating for review in reviews]) / len(reviews)
        return 0

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-created_at']

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} saved {self.recipe.title}"
    
    class Meta:
        unique_together = ['user', 'recipe']
        ordering = ['-saved_at']
        
