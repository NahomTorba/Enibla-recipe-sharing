from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from recipeApp.models import Recipe
from reviewApp.models import Review
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
