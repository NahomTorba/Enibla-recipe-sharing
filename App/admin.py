from django.contrib import admin
from .models import UserProfile, Recipe

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Recipe)