from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from recipeApp.models import Recipe, RecipeView



# constants
CUISINE_CHOICES = [ ('Ethiopian', 'Ethiopian'), ('Eritrea', 'Eritrea'), ('African', 'African'), ('Italian', 'Italian'),('Mexican', 'Mexican'),('Chinese', 'Chinese'),('Japanese', 'Japanese'),('Indian', 'Indian'),('French', 'French'),('American', 'American'),('Korean', 'Korean'),('Spanish', 'Spanish'),('Middle Eastern', 'Middle Eastern'),('Brazilian', 'Brazilian'),('British', 'British')]
TAG_CHOICES = (('breakfast', 'Breakfast'),('lunch', 'Lunch'),('dinner', 'Dinner'),('dessert', 'Dessert'),('snack', 'Snack'),('fasting', 'Fasting'),)


# Create your views here.

def index(request):
    """Home page view with featured and trending recipes and stats"""
    # Featured recipes (explicit flag)
    featured_recipes = Recipe.objects.filter(featured=True).select_related('author__user').order_by('-created_at')[:6]

    # Trending recipes: count views within last 7 days
    one_week_ago = timezone.now() - timedelta(days=7)
    recent_views = RecipeView.objects.filter(viewed_at__gte=one_week_ago)
    counts = {}
    for v in recent_views.values('recipe'):
        rid = v['recipe']
        counts[rid] = counts.get(rid, 0) + 1
    top_ids = sorted(counts.keys(), key=lambda rid: counts[rid], reverse=True)[:6]
    trending_recipes = list(Recipe.objects.filter(id__in=top_ids))
    trending_recipes.sort(key=lambda r: top_ids.index(r.id) if r.id in top_ids else 999)

    # Community stats
    total_recipes = Recipe.objects.count()
    total_users = User.objects.count()
    total_cuisines = len(CUISINE_CHOICES)
    total_favorites = 0

    context = {
        'featured_recipes': featured_recipes,
        'trending_recipes': trending_recipes,
        'total_recipes': total_recipes,
        'total_users': total_users,
        'total_cuisines': total_cuisines,
        'total_favorites': total_favorites,
    }
    return render(request, 'home.html', context)


