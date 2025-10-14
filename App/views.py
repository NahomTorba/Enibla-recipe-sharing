from django.shortcuts import render
from django.contrib.auth.models import User

from recipeApp.models import Recipe



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


