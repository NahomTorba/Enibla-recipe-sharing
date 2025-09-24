from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from recipeApp.models import Recipe
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import  Q
from django.core.paginator import Paginator
from userApp.models import UserProfile


# constants
CUISINE_CHOICES = [ ('Ethiopian', 'Ethiopian'), ('Eritrea', 'Eritrea'), ('African', 'African'), ('Italian', 'Italian'),('Mexican', 'Mexican'),('Chinese', 'Chinese'),('Japanese', 'Japanese'),('Indian', 'Indian'),('French', 'French'),('American', 'American'),('Korean', 'Korean'),('Spanish', 'Spanish'),('Middle Eastern', 'Middle Eastern'),('Brazilian', 'Brazilian'),('British', 'British')]
TAG_CHOICES = (('breakfast', 'Breakfast'),('lunch', 'Lunch'),('dinner', 'Dinner'),('dessert', 'Dessert'),('snack', 'Snack'),('fasting', 'Fasting'),)


# Create your views here.

def index(request):
    """Home page view with featured recipes and stats"""
    # Get featured recipes (latest 6)
    featured_recipes = Recipe.objects.select_related('author__user').order_by('-created_at')[:6]
    
    # Get community stats
    total_recipes = Recipe.objects.count()
    total_users = User.objects.count()
    total_cuisines = len(CUISINE_CHOICES)
    total_favorites = 0  # Placeholder for when favorites are implemented
    
    context = {
        'featured_recipes': featured_recipes,
        'total_recipes': total_recipes,
        'total_users': total_users,
        'total_cuisines': total_cuisines,
        'total_favorites': total_favorites,
    }
    return render(request, 'home.html', context)


