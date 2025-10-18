from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator


# User profile model from djangos User model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, blank=True, null=True)
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
