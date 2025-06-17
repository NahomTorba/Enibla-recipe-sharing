from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile, Recipe
from django.utils import timezone

# Create your tests here.

class UserProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Food lover.',
            favorite_cuisines='Ethiopian, Italian, Mexican'
        )

    def test_user_profile_str(self):
        self.assertEqual(str(self.profile), "testuser's Profile")

    def test_get_favorite_cuisines_list(self):
        expected = ['Ethiopian', 'Italian', 'Mexican']
        self.assertEqual(self.profile.get_favorite_cuisines_list(), expected)

class RecipeModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='chef', password='secret')
        self.profile = UserProfile.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.profile,
            title='Spaghetti Bolognese',
            description='Classic Italian dish',
            ingredients='Spaghetti, minced beef, tomato sauce',
            instructions='Boil spaghetti. Cook sauce. Mix.',
            tags='dinner, Italian'
        )

    def test_recipe_str(self):
        self.assertEqual(str(self.recipe), 'Spaghetti Bolognese')

    def test_get_tag_choices_list(self):
        expected = ['dinner', 'Italian']
        self.assertEqual(self.recipe.get_tag_choices_list(), expected)