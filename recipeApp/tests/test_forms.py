from django.test import TestCase
from django.contrib.auth.models import User
from userApp.models import UserProfile
from recipeApp.forms import RecipeForm


class RecipeFormTests(TestCase):
    def setUp(self):
        # Create a user and associated profile to be the recipe author.
        self.user = User.objects.create_user(username='testchef', password='strongpass')
        self.profile = UserProfile.objects.create(user=self.user)

    def test_valid_recipe_submission(self):
        """Ensure that the recipe form is valid for correct data."""
        form_data = {
            'author': self.profile.id,
            'title': 'Chocolate Cake',
            'description': 'Delicious and rich chocolate cake',
            'ingredients': 'Flour, eggs, chocolate, sugar, butter',
            'instructions': 'Mix ingredients and bake.',
            'tags': 'dessert, snack'
        }
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_recipe_submission_empty_fields(self):
        form_data = {
            'author': self.profile.id,
            'title': '',
            'description': '',
            'ingredients': '',
            'instructions': '',
            'tags': ''  
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('ingredients', form.errors)
        self.assertIn('instructions', form.errors)
