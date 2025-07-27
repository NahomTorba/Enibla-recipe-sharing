from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
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
    favorite_cuisines = models.CharField(max_length=200, blank=True)
    profile_image = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        super().clean()
        if self.favorite_cuisines:
            cuisines = self.favorite_cuisines.split(',')
            valid_cuisines = [choice[0] for choice in self.CUISINE_CHOICES]
            if not all(cuisine in valid_cuisines for cuisine in cuisines):
                raise ValidationError('Invalid cuisine choice(s) in favorite_cuisines')

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_favorite_cuisines_list(self):
        if self.favorite_cuisines:
            return self.favorite_cuisines.split(',')
        return []

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class Recipe(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    prep_time = models.IntegerField(default=0)
    cook_time = models.IntegerField(default=0)
    servings = models.IntegerField(default=1)
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
    views = models.IntegerField(default=0)

    def clean(self):
        super().clean()
        if self.tags:
            tags = self.tags.split(',')
            valid_tags = [choice[0] for choice in self.TAG_CHOICES]
            if not all(tag in valid_tags for tag in tags):
                raise ValidationError('Invalid tag choice(s) in tags')

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    @classmethod
    def get_trending_recipes(cls, limit=10):
        """Return recipes ordered by views count descending"""
        return cls.objects.all().order_by('-views')[:limit]

    def increment_views(self):
        """Increment the view count for this recipe"""
        self.views += 1
        self.save(update_fields=['views', 'updated_at'])

    def __str__(self):
        return self.title

    def get_tag_choices_list(self):
        if self.tags:
            return self.tags.split(',')
        return []

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'


class Review(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
