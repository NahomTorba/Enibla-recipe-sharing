from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.core.paginator import Paginator
from unittest.mock import patch, MagicMock
from recipeApp.models import Recipe, RecipeView
from userApp.models import UserProfile
from reviewApp.models import Review, SavedRecipe
from recipeApp.forms import RecipeForm


class RecipeAppViewsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user and profile
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            favorite_cuisines='Ethiopian,Italian'
        )
        
        # Create another user for testing permissions
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.other_profile = UserProfile.objects.create(
            user=self.other_user,
            bio='Other bio'
        )
        
        # Create test recipe
        self.recipe = Recipe.objects.create(
            author=self.user_profile,
            title='Test Recipe',
            description='A delicious test recipe',
            ingredients='2 cups flour\n1 cup sugar',
            instructions='Mix ingredients and bake',
            tags='breakfast,dessert',
            cuisine='Ethiopian',
            difficulty='Easy',
            prep_time=30
        )

    def test_create_recipe_get(self):
        """Test create recipe view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('create_recipe'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIsInstance(response.context['form'], RecipeForm)

    def test_create_recipe_post_valid(self):
        """Test create recipe view with valid POST data"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a simple image file for testing
        image = SimpleUploadedFile(
            "test_recipe.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )
        
        data = {
            'title': 'New Recipe',
            'description': 'A wonderful new recipe for testing',
            'ingredients': '2 cups flour\n1 cup sugar\n3 eggs',
            'instructions': 'Mix all ingredients together and bake for 30 minutes at 350°F',
            'cuisine': 'Italian',
            'difficulty': 'Medium',
            'prep_time': 45,
            'image': image,
            'tags': ['breakfast', 'lunch']
        }
        response = self.client.post(reverse('create_recipe'), data)
        
        # Check recipe was created
        self.assertTrue(Recipe.objects.filter(title='New Recipe').exists())
        new_recipe = Recipe.objects.get(title='New Recipe')
        self.assertEqual(new_recipe.author, self.user_profile)
        self.assertEqual(new_recipe.tags, 'breakfast,lunch')
        
        # Check redirect
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'slug': new_recipe.slug}))

    def test_create_recipe_post_invalid(self):
        """Test create recipe view with invalid POST data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': 'AB',  # Too short
            'description': 'Short',  # Too short
            'ingredients': 'Few',  # Too short
            'instructions': 'Brief',  # Too short
        }
        response = self.client.post(reverse('create_recipe'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Please correct the errors' in str(message) for message in messages))

    def test_create_recipe_unauthenticated(self):
        """Test create recipe view for unauthenticated user"""
        response = self.client.get(reverse('create_recipe'))
        self.assertRedirects(response, reverse('login'))

    def test_create_recipe_no_profile(self):
        """Test create recipe view for user without profile"""
        user_no_profile = User.objects.create_user(
            username='noprofile',
            email='noprofile@example.com',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        response = self.client.get(reverse('create_recipe'))
        self.assertRedirects(response, reverse('create_profile'))

    