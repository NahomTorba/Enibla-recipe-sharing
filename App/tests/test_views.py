from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from recipeApp.models import Recipe, RecipeView

class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('home')

        # Create test user
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create some recipes
        self.featured_recipe = Recipe.objects.create(
            title='Featured Recipe',
            description='A featured dish.',
            author=self.user,
            featured=True,
        )

        self.regular_recipe = Recipe.objects.create(
            title='Regular Recipe',
            description='Just a normal recipe.',
            author=self.user,
            featured=False,
        )

        # Create recent views for trending logic
        for _ in range(5):
            RecipeView.objects.create(
                recipe=self.regular_recipe,
                viewed_at=timezone.now()
            )

        # Create an older view (should not count as trending)
        RecipeView.objects.create(
            recipe=self.featured_recipe,
            viewed_at=timezone.now() - timedelta(days=10)
        )

    def test_index_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_index_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'home.html')

    def test_index_context_data(self):
        response = self.client.get(self.url)
        context = response.context

        self.assertIn('featured_recipes', context)
        self.assertIn('trending_recipes', context)
        self.assertIn('total_recipes', context)
        self.assertIn('total_users', context)
        self.assertIn('total_cuisines', context)
        self.assertIn('total_favorites', context)

        # Check values
        self.assertEqual(len(context['featured_recipes']), 1)
        self.assertEqual(len(context['trending_recipes']), 1)
        self.assertEqual(context['total_recipes'], 2)
        self.assertEqual(context['total_users'], 1)
        self.assertGreaterEqual(context['total_cuisines'], 1)
        self.assertEqual(context['total_favorites'], 0)
