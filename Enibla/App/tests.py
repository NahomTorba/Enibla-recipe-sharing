from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import UserProfile, Recipe
from datetime import timedelta
from django.utils import timezone

class RecipeTrendingTests(TestCase):
    def setUp(self):
        # Create test users and profiles
        user1 = User.objects.create_user(username='user1', password='password')
        user2 = User.objects.create_user(username='user2', password='password')
        
        self.profile1 = UserProfile.objects.create(user=user1)
        self.profile2 = UserProfile.objects.create(user=user2)
        
        # Create test recipes
        self.recipe1 = Recipe.objects.create(
            author=self.profile1,
            title='Recipe 1',
            description='Test recipe 1',
            ingredients='Ingredients 1',
            instructions='Instructions 1',
            prep_time=30,
            cook_time=60,
            servings=4,
            is_featured=False,
            tags='dinner'
        )
        
        self.recipe2 = Recipe.objects.create(
            author=self.profile2,
            title='Recipe 2',
            description='Test recipe 2',
            ingredients='Ingredients 2',
            instructions='Instructions 2',
            prep_time=20,
            cook_time=45,
            servings=2,
            is_featured=False,
            tags='lunch'
        )
        
        self.recipe3 = Recipe.objects.create(
            author=self.profile1,
            title='Recipe 3',
            description='Test recipe 3',
            ingredients='Ingredients 3',
            instructions='Instructions 3',
            prep_time=15,
            cook_time=30,
            servings=1,
            is_featured=True,
            tags='breakfast'
        )

    def test_get_trending_recipes(self):
        """Test that get_trending_recipes returns recipes sorted by views"""
        # Increment views for different recipes
        self.recipe1.increment_views()
        self.recipe1.increment_views()  # 2 views
        self.recipe2.increment_views()  # 1 view
        
        # Get trending recipes with limit 2
        trending = Recipe.get_trending_recipes(limit=2)
        
        # Verify sorting and limit
        self.assertEqual(len(trending), 2)
        self.assertEqual(trending[0], self.recipe1)  # Should be first with 2 views
        self.assertEqual(trending[1], self.recipe2)  # Should be second with 1 view

    def test_increment_views(self):
        """Test that increment_views properly updates view count"""
        initial_views = self.recipe1.views
        self.recipe1.increment_views()
        
        # Verify views increased by 1
        self.assertEqual(self.recipe1.views, initial_views + 1)
        
        # Verify only views and updated_at were updated
        recipe = Recipe.objects.get(id=self.recipe1.id)
        self.assertEqual(recipe.views, initial_views + 1)

    def test_recipe_detail_view_increment_views(self):
        """Test that recipe detail view increments views"""
        client = Client()
        
        # Get recipe detail view
        response = client.get(f'/recipes/{self.recipe1.slug}/')
        self.assertEqual(response.status_code, 200)
        
        # Verify views were incremented
        recipe = Recipe.objects.get(id=self.recipe1.id)
        self.assertEqual(recipe.views, 1)

    def test_index_view_trending_recipes(self):
        """Test that index view includes trending recipes"""
        client = Client()
        
        # Increment views for different recipes
        self.recipe1.increment_views()
        self.recipe2.increment_views()
        
        # Get index view
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Verify trending recipes are in context
        self.assertIn('trending_recipes', response.context)
        trending_recipes = response.context['trending_recipes']
        self.assertGreater(len(trending_recipes), 0)
        
        # Verify recipes are sorted by views
        if len(trending_recipes) > 1:
            self.assertGreaterEqual(
                trending_recipes[0].views,
                trending_recipes[1].views
            )
