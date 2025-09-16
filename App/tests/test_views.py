from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from App.models import Recipe, RecipeView, UserProfile
from datetime import timedelta
import random
import datetime

User = get_user_model()


class RecipeListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user and profile
        cls.user = User.objects.create_user(
            username="testuser", email="user@test.com", password="testpass123"
        )
        cls.user_profile = UserProfile.objects.create(user=cls.user, bio="Test Bio")

        # Create 25 recipes for pagination tests
        number_of_recipes = 25
        for i in range(number_of_recipes):
            Recipe.objects.create(
                author=cls.user_profile,
                title=f"Test Recipe {i}",
                slug=f"test-recipe-{i}",
                description=f"Description {i}",
                ingredients=f"Ingredient {i}",
                instructions=f"Step {i}",
                tags="breakfast" if i % 2 == 0 else "lunch",
                created_at=datetime.datetime.now() - datetime.timedelta(days=i)
            )

    def test_view_url_exists(self):
        """Test that recipe list URL returns status 200."""
        response = self.client.get(reverse("recipe_list"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the correct template is used."""
        response = self.client.get(reverse("recipe_list"))
        self.assertTemplateUsed(response, "recipes/recipe_list.html")

    def test_pagination_is_ten(self):
        """Test that pagination is set to 10 recipes per page."""
        response = self.client.get(reverse("recipe_list"))
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["recipe_list"]), 10)

    def test_lists_all_recipes(self):
        """Test that all recipes are returned on final page."""
        # Get last page (3rd page for 25 items with 10 per page)
        response = self.client.get(reverse("recipe_list") + "?page=3")
        self.assertEqual(len(response.context["recipe_list"]), 5)

    def test_recipe_ordering(self):
        """Test that recipes are ordered by most recent first."""
        response = self.client.get(reverse("recipe_list"))
        recipes = response.context["recipe_list"]
        
        # Verify descending order by creation date
        last_date = datetime.datetime.now().date()
        for recipe in recipes:
            self.assertLessEqual(recipe.created_at.date(), last_date)
            last_date = recipe.created_at.date()

    def test_recipe_display_content(self):
        """Test that recipe data is displayed correctly."""
        response = self.client.get(reverse("recipe_list"))
        content = response.content.decode()
        
        # Verify first page contains first 10 recipes
        for i in range(10):
            self.assertIn(f"Test Recipe {i}", content)
            self.assertIn(f"Description {i}", content)
            self.assertIn("Breakfast" if i % 2 == 0 else "Lunch", content)

        # Verify pagination controls
        self.assertIn("?page=2", content)  # Next page link
        self.assertIn("?page=3", content)  # Last page link

    def test_filter_by_tag(self):
        """Test that recipes can be filtered by tag."""
        # Filter breakfast recipes
        response = self.client.get(reverse("recipe_list") + "?tag=breakfast")
        content = response.content.decode()
        
        # Verify only breakfast recipes are shown
        recipes = response.context["recipe_list"]
        for recipe in recipes:
            self.assertEqual(recipe.tags, "breakfast")
        
        # Verify breakfast tag is highlighted
        self.assertIn('<a class="active" href="?tag=breakfast">Breakfast</a>', content)

        # Verify count matches (13 breakfast recipes: 0-24 even numbers)
        self.assertEqual(len(recipes), 13)
        self.assertIn("13 recipes", content)

    def test_invalid_page_parameter(self):
        """Test handling of invalid page parameters."""
        response = self.client.get(reverse("recipe_list") + "?page=999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 1)  # Falls back to first page

        response = self.client.get(reverse("recipe_list") + "?page=abc")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 1)

    def test_no_recipes_message(self):
        """Test empty state message when no recipes exist."""
        # Delete all recipes
        Recipe.objects.all().delete()
        
        response = self.client.get(reverse("recipe_list"))
        self.assertContains(response, "No recipes found")
        self.assertQuerysetEqual(response.context["recipe_list"], [])

class RecipeViewTrackingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = User.objects.create_user(username="user1", password="testpass")
        cls.user2 = User.objects.create_user(username="user2", password="testpass")
        cls.user_profile1 = UserProfile.objects.create(user=cls.user1)
        cls.user_profile2 = UserProfile.objects.create(user=cls.user2)
        
        # Create test recipes
        cls.recipe1 = Recipe.objects.create(
            author=cls.user_profile1,
            title="Recipe 1",
            slug="recipe-1",
            description="Description 1",
            ingredients="Ingredients 1",
            instructions="Instructions 1",
            tags="breakfast"
        )
        
        cls.recipe2 = Recipe.objects.create(
            author=cls.user_profile1,
            title="Recipe 2",
            slug="recipe-2",
            description="Description 2",
            ingredients="Ingredients 2",
            instructions="Instructions 2",
            tags="lunch"
        )
        
        cls.recipe3 = Recipe.objects.create(
            author=cls.user_profile2,
            title="Recipe 3",
            slug="recipe-3",
            description="Description 3",
            ingredients="Ingredients 3",
            instructions="Instructions 3",
            tags="dinner",
            featured=True
        )

    def test_view_count_increases_on_detail_view(self):
        """Test view count increases when recipe detail is accessed"""
        initial_views = self.recipe1.view_count
        self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe1.slug}))
        self.recipe1.refresh_from_db()
        self.assertEqual(self.recipe1.view_count, initial_views + 1)

    def test_view_record_created(self):
        """Test view record is created for each access"""
        view_count = RecipeView.objects.count()
        self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe1.slug}))
        self.assertEqual(RecipeView.objects.count(), view_count + 1)

    def test_anonymous_views_tracked(self):
        """Test anonymous users are tracked correctly"""
        client = Client()
        client.get(reverse('recipe_detail', kwargs={'slug': self.recipe1.slug}))
        view = RecipeView.objects.last()
        self.assertIsNone(view.user)
        self.assertEqual(view.recipe, self.recipe1)

    def test_logged_in_views_tracked(self):
        """Test logged-in users are tracked correctly"""
        self.client.force_login(self.user1)
        self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe1.slug}))
        view = RecipeView.objects.last()
        self.assertEqual(view.user, self.user1)
        self.assertEqual(view.recipe, self.recipe1)

    def test_multiple_views_from_same_user(self):
        """Test multiple views from same user create multiple records"""
        self.client.force_login(self.user1)
        
        # First view
        self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe1.slug}))
        first_view = RecipeView.objects.last()
        
        # Second view
        self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe1.slug}))
        second_view = RecipeView.objects.last()
        
        self.assertNotEqual(first_view.id, second_view.id)
        self.assertEqual(RecipeView.objects.filter(recipe=self.recipe1).count(), 2)

    def test_view_timestamp_recorded(self):
        """Test view timestamp is recorded accurately"""
        before_view = timezone.now()
        self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe1.slug}))
        after_view = timezone.now()
        
        view = RecipeView.objects.last()
        self.assertTrue(before_view <= view.viewed_at <= after_view)

    def test_view_count_in_context(self):
        """Test view count appears in template context"""
        response = self.client.get(reverse('recipe_detail', kwargs={'slug': self.recipe1.slug}))
        self.assertEqual(response.context['recipe'].view_count, self.recipe1.view_count)


class HomePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.user_profile = UserProfile.objects.create(user=cls.user)
        
        # Create test recipes
        cls.featured_recipe = Recipe.objects.create(
            author=cls.user_profile,
            title="Featured Recipe",
            slug="featured-recipe",
            description="Featured description",
            ingredients="Featured ingredients",
            instructions="Featured instructions",
            tags="featured",
            featured=True
        )
        
        # Create trending recipes with view history
        now = timezone.now()
        cls.trending_recipes = []
        
        # Recipe with many recent views
        cls.popular_recipe = Recipe.objects.create(
            author=cls.user_profile,
            title="Popular Recipe",
            slug="popular-recipe",
            description="Popular description",
            tags="trending"
        )
        for i in range(15):  # 15 recent views
            viewed_at = now - timedelta(hours=random.randint(0, 48))
            RecipeView.objects.create(
                recipe=cls.popular_recipe,
                viewed_at=viewed_at
            )
        
        # Recipe with some recent views
        cls.medium_recipe = Recipe.objects.create(
            author=cls.user_profile,
            title="Medium Recipe",
            slug="medium-recipe",
            description="Medium description",
            tags="trending"
        )
        for i in range(8):  # 8 recent views
            viewed_at = now - timedelta(hours=random.randint(0, 72))
            RecipeView.objects.create(
                recipe=cls.medium_recipe,
                viewed_at=viewed_at
            )
        
        # Recipe with old views only (shouldn't be trending)
        cls.old_recipe = Recipe.objects.create(
            author=cls.user_profile,
            title="Old Recipe",
            slug="old-recipe",
            description="Old description",
            tags="outdated"
        )
        for i in range(10):  # 10 old views
            viewed_at = now - timedelta(days=10)
            RecipeView.objects.create(
                recipe=cls.old_recipe,
                viewed_at=viewed_at
            )
        
        # Update view counts
        for recipe in Recipe.objects.all():
            recipe.view_count = RecipeView.objects.filter(recipe=recipe).count()
            recipe.save()

    def test_homepage_status(self):
        """Test homepage loads successfully"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_featured_recipes_section(self):
        """Test featured recipes section displays correctly"""
        response = self.client.get(reverse('home'))
        featured_recipes = response.context['featured_recipes']
        
        self.assertEqual(featured_recipes.count(), 1)
        self.assertEqual(featured_recipes[0], self.featured_recipe)
        self.assertContains(response, "Featured Recipe")
        self.assertContains(response, "featured-recipe")

    def test_trending_recipes_section(self):
        """Test trending recipes section displays correctly"""
        response = self.client.get(reverse('home'))
        trending_recipes = response.context['trending_recipes']
        
        # Should contain recipes with recent views
        self.assertEqual(trending_recipes.count(), 2)
        
        # Popular recipe should be first
        self.assertEqual(trending_recipes[0], self.popular_recipe)
        
        # Should contain medium recipe
        self.assertIn(self.medium_recipe, trending_recipes)
        
        # Should not contain recipe with only old views
        self.assertNotIn(self.old_recipe, trending_recipes)
        
        # Verify content display
        self.assertContains(response, "Popular Recipe")
        self.assertContains(response, "Medium Recipe")
        self.assertNotContains(response, "Old Recipe")

    def test_trending_order(self):
        """Test trending recipes are ordered by view count"""
        response = self.client.get(reverse('home'))
        trending_recipes = list(response.context['trending_recipes'])
        
        # Popular recipe should come before medium recipe
        self.assertEqual(trending_recipes[0], self.popular_recipe)
        self.assertEqual(trending_recipes[1], self.medium_recipe)
        
        # Verify view counts are correct
        self.assertEqual(trending_recipes[0].view_count, 15)
        self.assertEqual(trending_recipes[1].view_count, 8)

    def test_trending_time_window(self):
        """Test only views from last 7 days count for trending"""
        # Create a recipe with mixed view history
        recipe = Recipe.objects.create(
            author=self.user_profile,
            title="Mixed Views Recipe",
            slug="mixed-views",
            description="Mixed views description",
            tags="testing"
        )
        
        now = timezone.now()
        # Recent views (last 7 days)
        for i in range(5):
            RecipeView.objects.create(
                recipe=recipe,
                viewed_at=now - timedelta(days=random.randint(0, 6))
            )
        
        # Old views (beyond 7 days)
        for i in range(10):
            RecipeView.objects.create(
                recipe=recipe,
                viewed_at=now - timedelta(days=8))
        
        recipe.view_count = RecipeView.objects.filter(recipe=recipe).count()
        recipe.save()
        
        response = self.client.get(reverse('home'))
        trending_recipes = response.context['trending_recipes']
        
        # Should be included with 5 recent views
        self.assertIn(recipe, trending_recipes)
        self.assertEqual(trending_recipes.get(id=recipe.id).view_count, 5)

    def test_no_featured_recipes(self):
        """Test homepage without featured recipes"""
        # Remove featured flag
        self.featured_recipe.featured = False
        self.featured_recipe.save()
        
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['featured_recipes'].count(), 0)
        self.assertContains(response, "No featured recipes available")

    def test_no_trending_recipes(self):
        """Test homepage without trending recipes"""
        # Delete all recent views
        RecipeView.objects.all().delete()
        
        # Update view counts
        for recipe in Recipe.objects.all():
            recipe.view_count = 0
            recipe.save()
        
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['trending_recipes'].count(), 0)
        self.assertContains(response, "No trending recipes yet")

    def test_trending_limit(self):
        """Test trending recipes are limited to specified number"""
        # Create more trending recipes
        for i in range(10):
            recipe = Recipe.objects.create(
                author=self.user_profile,
                title=f"Trending Recipe {i}",
                slug=f"trending-{i}",
                description=f"Description {i}",
                tags=f"trending-{i}"
            )
            # Add recent views
            for j in range(5):
                RecipeView.objects.create(recipe=recipe)
            
            recipe.view_count = 5
            recipe.save()
        
        response = self.client.get(reverse('home'))
        trending_recipes = response.context['trending_recipes']
        
        # Should be limited to 6 recipes (or your configured limit)
        self.assertEqual(trending_recipes.count(), 6)
        
        # Should show highest view count recipes first
        self.assertEqual(trending_recipes[0].view_count, 15)  # Our popular recipe