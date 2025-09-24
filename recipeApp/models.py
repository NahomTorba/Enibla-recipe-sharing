from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image

# Create your models here.

class Recipe(models.Model):
    author = models.ForeignKey('userApp.UserProfile', on_delete=models.CASCADE, related_name='recipes')
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

    # New fields for filtering
    CUISINE_CHOICES = [
        ('Ethiopian', 'Ethiopian'), ('Eritrea', 'Eritrea'), ('African', 'African'), ('Italian', 'Italian'),
        ('Mexican', 'Mexican'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese'), ('Indian', 'Indian'),
        ('French', 'French'), ('American', 'American'), ('Korean', 'Korean'), ('Spanish', 'Spanish'),
        ('Middle Eastern', 'Middle Eastern'), ('Brazilian', 'Brazilian'), ('British', 'British')
    ]
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    cuisine = models.CharField(max_length=30, choices=CUISINE_CHOICES, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, blank=True)
    prep_time = models.PositiveIntegerField(null=True, blank=True, help_text="Preparation time in minutes")

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
        return f"{self.title} ({self.cuisine or 'No Cuisine'}, {self.difficulty or 'No Difficulty'}, {self.prep_time or '?'} min)"

    def get_absolute_url(self):
        return reverse('recipe_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('recipe_update', kwargs={'slug': self.slug})

    @property
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
        return list(tag_list)

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
