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

    def test_edit_recipe_get(self):
        """Test edit recipe view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_recipe', kwargs={'slug': self.recipe.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIn('recipe_tags', response.context)

    def test_edit_recipe_post_valid(self):
        """Test edit recipe view with valid POST data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': 'Updated Recipe',
            'description': 'An updated description for the recipe',
            'ingredients': '3 cups flour\n2 cups sugar\n4 eggs',
            'instructions': 'Updated instructions: Mix all ingredients and bake for 45 minutes',
            'cuisine': 'Mexican',
            'difficulty': 'Hard',
            'prep_time': 60,
            'tags': ['dinner', 'snack']
        }
        response = self.client.post(reverse('edit_recipe', kwargs={'slug': self.recipe.slug}), data)
        
        # Check recipe was updated
        updated_recipe = Recipe.objects.get(slug=self.recipe.slug)
        self.assertEqual(updated_recipe.title, 'Updated Recipe')
        self.assertEqual(updated_recipe.cuisine, 'Mexican')
        self.assertEqual(updated_recipe.tags, 'dinner,snack')
        
        # Check redirect
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))

    def test_edit_recipe_post_invalid(self):
        """Test edit recipe view with invalid POST data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': 'AB',  # Too short
            'description': 'Short',  # Too short
            'ingredients': 'Few',  # Too short
            'instructions': 'Brief',  # Too short
        }
        response = self.client.post(reverse('edit_recipe', kwargs={'slug': self.recipe.slug}), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Please correct the errors' in str(message) for message in messages))

    def test_edit_recipe_unauthorized_user(self):
        """Test edit recipe view for unauthorized user"""
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('edit_recipe', kwargs={'slug': self.recipe.slug}))
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("You don't have permission" in str(message) for message in messages))

    def test_edit_recipe_not_found(self):
        """Test edit recipe view for non-existing recipe"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_recipe', kwargs={'slug': 'non-existent'}))
        self.assertRedirects(response, reverse('index'))

    def test_delete_recipe_get(self):
        """Test delete recipe view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('delete_recipe', kwargs={'slug': self.recipe.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)

    def test_delete_recipe_post(self):
        """Test delete recipe view POST request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('delete_recipe', kwargs={'slug': self.recipe.slug}))
        
        # Check recipe was deleted
        self.assertFalse(Recipe.objects.filter(slug=self.recipe.slug).exists())
        
        # Check redirect
        self.assertRedirects(response, reverse('index'))

    def test_delete_recipe_unauthorized_user(self):
        """Test delete recipe view for unauthorized user"""
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('delete_recipe', kwargs={'slug': self.recipe.slug}))
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("You can only delete your own recipes" in str(message) for message in messages))

    def test_delete_recipe_not_found(self):
        """Test delete recipe view for non-existing recipe"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('delete_recipe', kwargs={'slug': 'non-existent'}))
        self.assertRedirects(response, reverse('index'))

    def test_recipe_detail_authenticated(self):
        """Test recipe detail view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertContains(response, self.recipe.description)
        self.assertIn('recipe', response.context)
        self.assertIn('reviews', response.context)
        self.assertIn('is_saved', response.context)

    def test_recipe_detail_unauthenticated(self):
        """Test recipe detail view for unauthenticated user"""
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertIn('recipe', response.context)

    def test_recipe_detail_view_tracking(self):
        """Test recipe detail view tracking"""
        initial_views = self.recipe.view_count
        
        # Test authenticated user view
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        self.assertEqual(response.status_code, 200)
        
        # Check view count increased
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.view_count, initial_views + 1)
        
        # Check RecipeView was created
        self.assertTrue(RecipeView.objects.filter(recipe=self.recipe, user=self.user).exists())

    def test_recipe_detail_view_tracking_unauthenticated(self):
        """Test recipe detail view tracking for unauthenticated user"""
        initial_views = self.recipe.view_count
        
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        self.assertEqual(response.status_code, 200)
        
        # Check view count increased
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.view_count, initial_views + 1)
        
        # Check RecipeView was created with no user
        self.assertTrue(RecipeView.objects.filter(recipe=self.recipe, user=None).exists())

    def test_recipe_detail_saved_recipe(self):
        """Test recipe detail view with saved recipe"""
        # Create a saved recipe
        SavedRecipe.objects.create(user=self.user, recipe=self.recipe)
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_saved'])

    def test_recipe_detail_with_reviews(self):
        """Test recipe detail view with reviews"""
        # Create a review
        review = Review.objects.create(
            user=self.user,
            recipe=self.recipe,
            rating=5,
            comment='Great recipe!'
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('reviews', response.context)
        self.assertEqual(len(response.context['reviews']), 1)
        self.assertTrue(response.context['has_reviewed'])

    def test_recipe_list_view_basic(self):
        """Test recipe list view basic functionality"""
        response = self.client.get(reverse('recipe_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertIn('recipes', response.context)
        self.assertIn('total_recipes', response.context)

    def test_recipe_list_view_search(self):
        """Test recipe list view with search query"""
        response = self.client.get(reverse('recipe_list'), {'q': 'Test'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertEqual(response.context['search_query'], 'Test')

    def test_recipe_list_view_search_no_results(self):
        """Test recipe list view with search query that returns no results"""
        response = self.client.get(reverse('recipe_list'), {'q': 'nonexistent'})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.recipe.title)
        self.assertEqual(response.context['total_recipes'], 0)

    def test_recipe_list_view_cuisine_filter(self):
        """Test recipe list view with cuisine filter"""
        response = self.client.get(reverse('recipe_list'), {'cuisine': 'Ethiopian'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertEqual(response.context['selected_cuisine'], 'Ethiopian')

    def test_recipe_list_view_difficulty_filter(self):
        """Test recipe list view with difficulty filter"""
        response = self.client.get(reverse('recipe_list'), {'difficulty': 'Easy'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertEqual(response.context['selected_difficulty'], 'Easy')

    def test_recipe_list_view_prep_time_filter(self):
        """Test recipe list view with prep time filter"""
        response = self.client.get(reverse('recipe_list'), {'prep_time': '45'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertEqual(response.context['selected_prep_time'], '45')

    def test_recipe_list_view_tag_filter(self):
        """Test recipe list view with tag filter"""
        response = self.client.get(reverse('recipe_list'), {'tag': 'breakfast'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertIn('breakfast', response.context['selected_tags'])

    def test_recipe_list_view_multiple_tag_filter(self):
        """Test recipe list view with multiple tag filters"""
        response = self.client.get(reverse('recipe_list'), {'tag': ['breakfast', 'dessert']})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertIn('breakfast', response.context['selected_tags'])
        self.assertIn('dessert', response.context['selected_tags'])

    def test_recipe_list_view_pagination(self):
        """Test recipe list view pagination"""
        # Create multiple recipes to test pagination
        for i in range(15):
            Recipe.objects.create(
                author=self.user_profile,
                title=f'Recipe {i}',
                description=f'Description {i}',
                ingredients=f'Ingredients {i}',
                instructions=f'Instructions {i}',
                tags='breakfast'
            )
        
        response = self.client.get(reverse('recipe_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertIn('page_obj', response.context)

    def test_recipe_list_view_invalid_page(self):
        """Test recipe list view with invalid page number"""
        response = self.client.get(reverse('recipe_list'), {'page': '999'})
        
        self.assertEqual(response.status_code, 200)
        # Should redirect to page 1
        self.assertEqual(response.context['page_obj'].number, 1)

    def test_recipe_list_view_combined_filters(self):
        """Test recipe list view with combined filters"""
        response = self.client.get(reverse('recipe_list'), {
            'q': 'Test',
            'cuisine': 'Ethiopian',
            'difficulty': 'Easy',
            'prep_time': '30',
            'tag': 'breakfast'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertEqual(response.context['search_query'], 'Test')
        self.assertEqual(response.context['selected_cuisine'], 'Ethiopian')
        self.assertEqual(response.context['selected_difficulty'], 'Easy')
        self.assertEqual(response.context['selected_prep_time'], '30')
        self.assertIn('breakfast', response.context['selected_tags'])

    def test_recipe_list_view_no_pagination_with_tags(self):
        """Test recipe list view pagination disabled with tag filters"""
        response = self.client.get(reverse('recipe_list'), {'tag': 'breakfast'})
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_paginated'])

    def test_recipe_detail_related_recipes(self):
        """Test recipe detail view shows related recipes"""
        # Create related recipes
        related_recipe1 = Recipe.objects.create(
            author=self.user_profile,
            title='Related Recipe 1',
            description='Related description 1',
            ingredients='Related ingredients 1',
            instructions='Related instructions 1',
            tags='breakfast,dessert'  # Same tags
        )
        
        related_recipe2 = Recipe.objects.create(
            author=self.user_profile,
            title='Related Recipe 2',
            description='Related description 2',
            ingredients='Related ingredients 2',
            instructions='Related instructions 2',
            tags='lunch'  # Different tags
        )
        
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('related_recipes', response.context)
        # Should include the recipe with same tags
        self.assertIn(related_recipe1, response.context['related_recipes'])

    def test_recipe_detail_average_rating(self):
        """Test recipe detail view shows average rating"""
        # Create reviews with different ratings
        Review.objects.create(user=self.user, recipe=self.recipe, rating=5, comment='Great!')
        Review.objects.create(user=self.other_user, recipe=self.recipe, rating=3, comment='Good')
        
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('average_rating', response.context)
        self.assertEqual(response.context['average_rating'], 4.0)  # (5 + 3) / 2

    def test_recipe_detail_no_rating(self):
        """Test recipe detail view with no reviews"""
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['average_rating'], 0)

    def test_recipe_detail_image_url(self):
        """Test recipe detail view includes image URL"""
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('image_url', response.context)
        # Image URL should be None since no image is uploaded
        self.assertIsNone(response.context['image_url'])

    def test_recipe_detail_editing_review_session(self):
        """Test recipe detail view with editing review in session"""
        # Create a review
        review = Review.objects.create(
            user=self.user,
            recipe=self.recipe,
            rating=4,
            comment='Original comment'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Set editing session
        session = self.client.session
        session['editing_review_id'] = str(review.id)
        session.save()
        
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_editing'])
        self.assertEqual(response.context['user_review'], review)
