from django.contrib import admin
from .models import UserProfile, Recipe, Review

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Recipe)
admin.site.register(Review)