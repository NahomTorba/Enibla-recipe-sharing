from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from recipeApp.models import Recipe
from reviewApp.models import Review, SavedRecipe
from django.contrib.messages import get_messages

class AddReviewTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.recipe = Recipe.objects.create(title="Test Recipe", slug="test-recipe")
        self.client.login(username='testuser', password='testpassword')

    def test_add_review(self):
        """Test adding a new review"""
        url = reverse('add_review', kwargs={'slug': self.recipe.slug})
        response = self.client.post(url, data={'rating': 5, 'comment': 'Great recipe!'})
        
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        self.assertTrue(Review.objects.filter(user=self.user, recipe=self.recipe).exists())
        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Your review has been added!')

    def test_update_review(self):
        """Test updating an existing review"""
        Review.objects.create(user=self.user, recipe=self.recipe, rating=3, comment='Okay recipe.')
        url = reverse('add_review', kwargs={'slug': self.recipe.slug})
        response = self.client.post(url, data={'rating': 5, 'comment': 'Great recipe!'})

        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        review = Review.objects.get(user=self.user, recipe=self.recipe)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great recipe!')
        # Verify success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Your review has been updated!')

    def test_review_form_invalid(self):
        """Test submitting an invalid review form"""
        url = reverse('add_review', kwargs={'slug': self.recipe.slug})
        response = self.client.post(url, data={'rating': '', 'comment': ''})

        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'slug': self.recipe.slug}))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)


    def test_edit_review_logged_in_user(self):
        # Setup
        user = User.objects.create_user(username='testuser', password='password')
        recipe = Recipe.objects.create(title='Test Recipe', slug='test-recipe')
        review = Review.objects.create(user=user, recipe=recipe, content='Great recipe!')
        self.client.login(username='testuser', password='password')
        
        # Test
        response = self.client.get(reverse('edit_review', kwargs={'review_id': review.id}))
        
        # Assertions
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'slug': recipe.slug}))
        self.assertEqual(response.cookies['sessionid'].value, 'editing_review_id')
        self.assertIn('You can now update your review below.', response.cookies['messages'])

    def test_edit_review_other_user(self):
        # Setup
        user1 = User.objects.create_user(username='user1', password='password')
        user2 = User.objects.create_user(username='user2', password='password')
        recipe = Recipe.objects.create(title='Test Recipe', slug='test-recipe')
        review = Review.objects.create(user=user1, recipe=recipe, content='Great recipe!')
        self.client.login(username='user2', password='password')
        
        # Test
        response = self.client.get(reverse('edit_review', kwargs={'review_id': review.id}))
        
        # Assertions
        self.assertEqual(response.status_code, 403)  # Forbidden (user2 cannot edit user1's review)

    def test_delete_review_logged_in_user(self):
        # Setup
        user = User.objects.create_user(username='testuser', password='password')
        recipe = Recipe.objects.create(title='Test Recipe', slug='test-recipe')
        review = Review.objects.create(user=user, recipe=recipe, content='Great recipe!')
        self.client.login(username='testuser', password='password')
        
        # Test
        response = self.client.post(reverse('delete_review', kwargs={'review_id': review.id}))
        
        # Assertions
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'slug': recipe.slug}))
        self.assertFalse(Review.objects.filter(id=review.id).exists())  # Ensure the review is deleted
        self.assertIn('Your review has been deleted!', response.cookies['messages'])

    def test_delete_review_other_user(self):
        # Setup
        user1 = User.objects.create_user(username='user1', password='password')
        user2 = User.objects.create_user(username='user2', password='password')
        recipe = Recipe.objects.create(title='Test Recipe', slug='test-recipe')
        review = Review.objects.create(user=user1, recipe=recipe, content='Great recipe!')
        self.client.login(username='user2', password='password')
        
        # Test
        response = self.client.post(reverse('delete_review', kwargs={'review_id': review.id}))
        
        # Assertions
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'slug': recipe.slug}))
        self.assertIn('You can only delete your own reviews.', response.cookies['messages'])

class SaveRecipeTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.recipe = Recipe.objects.create(name='Test Recipe', slug='test-recipe')

    def test_save_recipe_create(self):
        """Test saving a recipe to the user's saved recipes"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('save_recipe', kwargs={'slug': self.recipe.slug}))
        
        # Check the response and database state
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Recipe saved!')
        self.assertTrue(SavedRecipe.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_save_recipe_unsave(self):
        """Test unsaving a recipe from the user's saved recipes"""
        SavedRecipe.objects.create(user=self.user, recipe=self.recipe)  # Create a saved recipe

        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('save_recipe', kwargs={'slug': self.recipe.slug}))
        
        # Check the response and database state
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Recipe removed from saved recipes.')
        self.assertFalse(SavedRecipe.objects.filter(user=self.user, recipe=self.recipe).exists())

class CheckSavedRecipeTestCase(TestCase):
    def setUp(self):
        # Create a test user and recipe
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.recipe = Recipe.objects.create(name='Test Recipe', slug='test-recipe')

    def test_check_saved_recipe_true(self):
        """Test that the recipe is marked as saved for the user"""
        SavedRecipe.objects.create(user=self.user, recipe=self.recipe)  # Create a saved recipe
        
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('check_saved_recipe', kwargs={'slug': self.recipe.slug}))
        
        # Check that the recipe is saved
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_saved'])

    def test_check_saved_recipe_false(self):
        """Test that the recipe is not marked as saved for the user"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('check_saved_recipe', kwargs={'slug': self.recipe.slug}))
        
        # Check that the recipe is not saved
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_saved'])

class UnsaveRecipeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='password123')
        self.recipe = Recipe.objects.create(title='Test Recipe', slug='test-recipe')
        self.url = reverse('unsave_recipe', args=[self.recipe.slug])

    def test_unsave_recipe_success(self):
        """User successfully unsaves a recipe."""
        SavedRecipe.objects.create(user=self.user, recipe=self.recipe)

        self.client.login(username='tester', password='password123')
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Recipe unsaved successfully.')

        # Ensure the SavedRecipe was deleted
        self.assertFalse(SavedRecipe.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_unsave_recipe_not_found_in_saved(self):
        """User tries to unsave a recipe they haven’t saved."""
        self.client.login(username='tester', password='password123')
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Recipe not found in saved recipes.')

    def test_unsave_recipe_requires_login(self):
        """Anonymous users are redirected to login."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertIn('/login', response.url)

    def test_unsave_recipe_disallows_get(self):
        """The view should reject non-POST requests."""
        self.client.login(username='tester', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed