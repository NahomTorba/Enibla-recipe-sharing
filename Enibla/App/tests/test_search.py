from django.test import TestCase
from django.urls import reverse
from App.models import Recipe, UserProfile
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()

class RecipeSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user and profile
        cls.user = User.objects.create_user(
            username="testuser", email="user@test.com", password="testpass123"
        )
        cls.user_profile = UserProfile.objects.create(user=cls.user, bio="Test Bio")
        
        # Create test recipes with varied content
        cls.recipe1 = Recipe.objects.create(
            author=cls.user_profile,
            title="Chocolate Cake",
            slug="chocolate-cake",
            description="Decadent chocolate dessert",
            ingredients="flour, sugar, cocoa powder, eggs, chocolate",
            instructions="Mix dry ingredients\nAdd wet ingredients\nBake at 350°F",
            tags="dessert,baking",
            created_at=datetime.datetime.now() - datetime.timedelta(days=5))
        
        cls.recipe2 = Recipe.objects.create(
            author=cls.user_profile,
            title="Vegetable Stir Fry",
            slug="vegetable-stir-fry",
            description="Healthy Asian-inspired dish",
            ingredients="broccoli, carrots, soy sauce, tofu, ginger",
            instructions="Chop vegetables\nStir fry with sauce",
            tags="lunch,vegan,healthy",
            created_at=datetime.datetime.now() - datetime.timedelta(days=3))
        
        cls.recipe3 = Recipe.objects.create(
            author=cls.user_profile,
            title="Chocolate Chip Cookies",
            slug="chocolate-chip-cookies",
            description="Classic cookie recipe",
            ingredients="flour, sugar, chocolate chips, butter, eggs",
            instructions="Cream butter and sugar\nAdd flour\nBake at 375°F",
            tags="snack,dessert,baking",
            created_at=datetime.datetime.now() - datetime.timedelta(days=1))

    def test_search_by_title(self):
        """Test searching by recipe title"""
        response = self.client.get(reverse("recipe_list"), {"q": "chocolate"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        # Should return both chocolate recipes
        self.assertIn("Chocolate Cake", content)
        self.assertIn("Chocolate Chip Cookies", content)
        self.assertNotIn("Vegetable Stir Fry", content)
        
        # Verify search result count
        self.assertIn("2 recipes found", content)

    def test_search_by_ingredient(self):
        """Test searching by ingredient name"""
        response = self.client.get(reverse("recipe_list"), {"q": "tofu"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        # Should return stir fry recipe
        self.assertIn("Vegetable Stir Fry", content)
        self.assertNotIn("Chocolate Cake", content)
        self.assertNotIn("Chocolate Chip Cookies", content)

    def test_search_by_tag(self):
        """Test searching by tag name"""
        response = self.client.get(reverse("recipe_list"), {"q": "baking"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        # Should return both baking recipes
        self.assertIn("Chocolate Cake", content)
        self.assertIn("Chocolate Chip Cookies", content)
        self.assertNotIn("Vegetable Stir Fry", content)

    def test_search_multiple_fields(self):
        """Test search matches across multiple fields"""
        response = self.client.get(reverse("recipe_list"), {"q": "sugar"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        # Should return both recipes containing "sugar"
        self.assertIn("Chocolate Cake", content)
        self.assertIn("Chocolate Chip Cookies", content)
        self.assertNotIn("Vegetable Stir Fry", content)

    def test_case_insensitive_search(self):
        """Test search is case-insensitive"""
        response = self.client.get(reverse("recipe_list"), {"q": "CHOCOLATE"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Chocolate Cake", content)
        self.assertIn("Chocolate Chip Cookies", content)

    def test_partial_word_search(self):
        """Test partial word matching"""
        response = self.client.get(reverse("recipe_list"), {"q": "choco"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Chocolate Cake", content)
        self.assertIn("Chocolate Chip Cookies", content)

    def test_empty_search_query(self):
        """Test empty search query returns all recipes"""
        response = self.client.get(reverse("recipe_list"), {"q": ""})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Chocolate Cake", content)
        self.assertIn("Vegetable Stir Fry", content)
        self.assertIn("Chocolate Chip Cookies", content)
        self.assertIn("3 recipes found", content)

    def test_no_search_results(self):
        """Test search with no matching results"""
        response = self.client.get(reverse("recipe_list"), {"q": "pizza"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        
        # Verify no recipes displayed
        self.assertNotIn("Chocolate Cake", content)
        self.assertNotIn("Vegetable Stir Fry", content)
        self.assertNotIn("Chocolate Chip Cookies", content)
        
        # Verify empty state message
        self.assertIn("No recipes found matching", content)
        self.assertIn("pizza", content)

    def test_special_characters_in_search(self):
        """Test search handles special characters"""
        # Search with special character
        response = self.client.get(reverse("recipe_list"), {"q": "350°F"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Chocolate Cake", content)
        
        # Search with HTML characters
        response = self.client.get(reverse("recipe_list"), {"q": "<script>"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("No recipes found", content)

    def test_whitespace_handling(self):
        """Test search handles leading/trailing whitespace"""
        response = self.client.get(reverse("recipe_list"), {"q": "  chocolate  "})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Chocolate Cake", content)
        self.assertIn("Chocolate Chip Cookies", content)