from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import UserProfile, Recipe
from .forms import RecipeForm

# Create your tests here.

class RecipeModelTests(TestCase):
    def setUp(self):
        # Create a user and associated profile for testing
        self.user = User.objects.create_user(username='chef', password='securepass')
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            favorite_cuisines='Ethiopian, Italian'
        )

        # Create the sample Recipe instance
        self.recipe = Recipe.objects.create(
            author=self.profile,
            title='Spaghetti Bolognese',
            description='A classic Italian dish.',
            ingredients='Spaghetti, minced beef, tomato sauce',
            instructions='Boil spaghetti. Cook sauce. Mix together.',
            tags='dinner, Italian'
        )

    def test_recipe_str(self):
        """Test that the Recipe __str__ returns the title."""
        self.assertEqual(str(self.recipe), 'Spaghetti Bolognese')

    def test_get_tag_choices_list(self):
        """Test that the helper method splits the tags correctly."""
        expected = ['dinner', ' Italian']
        self.assertEqual(self.recipe.get_tag_choices_list(), expected)

    def test_recipe_image_upload(self):
        """Test image upload handling in the Recipe model."""
        image_data = SimpleUploadedFile("test.jpg", b"fake_image_data", content_type="image/jpeg")
        recipe_with_image = Recipe.objects.create(
            author=self.profile,
            title='Recipe with Image',
            description='Testing image upload functionality.',
            ingredients='Ingredients list',
            instructions='Instructions here',
            tags='breakfast',
            image=image_data
        )
        self.assertTrue(recipe_with_image.image)


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