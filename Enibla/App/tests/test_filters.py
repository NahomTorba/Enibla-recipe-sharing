from django.test import TestCase
from django.urls import reverse
from App.models import Recipe, UserProfile
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()

class RecipeFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user and profile
        cls.user = User.objects.create_user(
            username="testuser", email="user@test.com", password="testpass123"
        )
        cls.user_profile = UserProfile.objects.create(user=cls.user, bio="Test Bio")
        
        # Create test recipes with varied tags
        cls.breakfast_recipe = Recipe.objects.create(
            author=cls.user_profile,
            title="Avocado Toast",
            slug="avocado-toast",
            description="Simple breakfast recipe",
            ingredients="bread, avocado, salt",
            instructions="Toast bread\nMash avocado\nAdd salt",
            tags="breakfast,vegetarian,quick",
            created_at=datetime.datetime.now() - datetime.timedelta(days=5))
        
        cls.lunch_recipe = Recipe.objects.create(
            author=cls.user_profile,
            title="Chicken Salad",
            slug="chicken-salad",
            description="Healthy lunch option",
            ingredients="chicken, lettuce, tomatoes, dressing",
            instructions="Mix ingredients\nAdd dressing",
            tags="lunch,healthy",
            created_at=datetime.datetime.now() - datetime.timedelta(days=3))
        
        cls.dinner_recipe = Recipe.objects.create(
            author=cls.user_profile,
            title="Beef Stir Fry",
            slug="beef-stir-fry",
            description="Quick dinner solution",
            ingredients="beef, broccoli, soy sauce, rice",
            instructions="Stir fry beef\nAdd vegetables\nServe with rice",
            tags="dinner,quick,meat",
            created_at=datetime.datetime.now() - datetime.timedelta(days=1))
        
        cls.dessert_recipe = Recipe.objects.create(
            author=cls.user_profile,
            title="Chocolate Mousse",
            slug="chocolate-mousse",
            description="Rich chocolate dessert",
            ingredients="chocolate, cream, sugar",
            instructions="Melt chocolate\nWhip cream\nCombine",
            tags="dessert,vegetarian",
            created_at=datetime.datetime.now() - datetime.timedelta(days=2))

    def test_single_filter(self):
        """Test filtering by a single tag"""
        response = self.client.get(reverse("recipe_list"), {"tag": "breakfast"})
        content = response.content.decode()
        
        self.assertIn("Avocado Toast", content)
        self.assertNotIn("Chicken Salad", content)
        self.assertNotIn("Beef Stir Fry", content)
        self.assertNotIn("Chocolate Mousse", content)
        
        # Verify active filter highlighting
        self.assertIn('<a class="active" href="?tag=breakfast">Breakfast</a>', content)

    def test_multiple_filters(self):
        """Test combining multiple filters with AND logic"""
        response = self.client.get(reverse("recipe_list"), {"tag": ["vegetarian", "quick"]})
        content = response.content.decode()
        
        # Should return only recipes with BOTH tags
        self.assertIn("Avocado Toast", content)  # Has both tags
        self.assertNotIn("Chocolate Mousse", content)  # Only vegetarian
        self.assertNotIn("Beef Stir Fry", content)  # Only quick
        self.assertNotIn("Chicken Salad", content)  # Neither
        
        # Verify both active filters are highlighted
        self.assertIn('?tag=vegetarian" class="active">Vegetarian</a>', content)
        self.assertIn('?tag=quick" class="active">Quick</a>', content)

    def test_filter_combinations(self):
        """Test various filter combinations"""
        # Vegetarian desserts
        response = self.client.get(reverse("recipe_list"), {"tag": ["vegetarian", "dessert"]})
        content = response.content.decode()
        self.assertIn("Chocolate Mousse", content)
        self.assertNotIn("Avocado Toast", content)
        
        # Quick meals (both breakfast and dinner)
        response = self.client.get(reverse("recipe_list"), {"tag": "quick"})
        content = response.content.decode()
        self.assertIn("Avocado Toast", content)
        self.assertIn("Beef Stir Fry", content)
        self.assertNotIn("Chicken Salad", content)

    def test_no_filters(self):
        """Test no filters returns all recipes"""
        response = self.client.get(reverse("recipe_list"))
        content = response.content.decode()
        
        self.assertIn("Avocado Toast", content)
        self.assertIn("Chicken Salad", content)
        self.assertIn("Beef Stir Fry", content)
        self.assertIn("Chocolate Mousse", content)
        
        # Verify no active filters
        self.assertNotIn('class="active"', content)

    def test_invalid_filter(self):
        """Test invalid filter tag is ignored"""
        response = self.client.get(reverse("recipe_list"), {"tag": "invalid"})
        content = response.content.decode()
        
        # Should return all recipes (invalid filter ignored)
        self.assertIn("Avocado Toast", content)
        self.assertIn("Chicken Salad", content)
        self.assertIn("Beef Stir Fry", content)
        self.assertIn("Chocolate Mousse", content)

    def test_filter_with_search(self):
        """Test combining search query with filters"""
        # Search for "chocolate" in vegetarian desserts
        response = self.client.get(reverse("recipe_list"), {
            "q": "chocolate",
            "tag": ["vegetarian", "dessert"]
        })
        content = response.content.decode()
        
        self.assertIn("Chocolate Mousse", content)
        self.assertNotIn("Avocado Toast", content)  # Matches filters but not search
        
        # Search for "toast" in breakfast recipes
        response = self.client.get(reverse("recipe_list"), {
            "q": "toast",
            "tag": "breakfast"
        })
        content = response.content.decode()
        self.assertIn("Avocado Toast", content)
        self.assertNotIn("Beef Stir Fry", content)

    def test_empty_results(self):
        """Test filter combination that returns no results"""
        response = self.client.get(reverse("recipe_list"), {"tag": ["meat", "vegetarian"]})
        content = response.content.decode()
        
        # Verify no recipes displayed
        self.assertNotIn("Avocado Toast", content)
        self.assertNotIn("Chicken Salad", content)
        self.assertNotIn("Beef Stir Fry", content)
        self.assertNotIn("Chocolate Mousse", content)
        
        # Verify empty state message
        self.assertIn("No recipes found matching the selected filters", content)
        
        # Verify active filters still show
        self.assertIn('?tag=meat" class="active">Meat</a>', content)
        self.assertIn('?tag=vegetarian" class="active">Vegetarian</a>', content)

    def test_filter_removal(self):
        """Test removing filters from current selection"""
        # Start with two filters
        response = self.client.get(reverse("recipe_list"), {"tag": ["vegetarian", "quick"]})
        content = response.content.decode()
        self.assertIn("Avocado Toast", content)
        
        # Remove "quick" filter by clicking its active state
        # This would generate URL: ?tag=vegetarian
        remove_quick_url = reverse("recipe_list") + "?tag=vegetarian"
        self.assertIn(f'href="{remove_quick_url}"', content)

    def test_special_characters_in_filters(self):
        """Test filters with special characters in tag names"""
        # Create recipe with special character tag
        recipe = Recipe.objects.create(
            author=self.user_profile,
            title="Gluten-Free Bread",
            slug="gluten-free-bread",
            description="Allergy-friendly recipe",
            ingredients="gluten-free flour, yeast, water",
            instructions="Mix ingredients\nBake",
            tags="gluten-free,special-diet",
        )
        
        response = self.client.get(reverse("recipe_list"), {"tag": "gluten-free"})
        content = response.content.decode()
        self.assertIn("Gluten-Free Bread", content)
        self.assertIn('Gluten-Free', content)  # Properly displayed

    def test_filter_counts(self):
        """Test displayed counts for each filter option"""
        response = self.client.get(reverse("recipe_list"))
        content = response.content.decode()
        
        # Verify counts reflect all recipes
        self.assertIn('Breakfast <span class="count">(1)</span>', content)
        self.assertIn('Lunch <span class="count">(1)</span>', content)
        self.assertIn('Dinner <span class="count">(1)</span>', content)
        self.assertIn('Dessert <span class="count">(1)</span>', content)
        self.assertIn('Vegetarian <span class="count">(2)</span>', content)
        self.assertIn('Quick <span class="count">(2)</span>', content)
        
        # Test counts update with active filters
        response = self.client.get(reverse("recipe_list"), {"tag": "vegetarian"})
        content = response.content.decode()
        self.assertIn('Breakfast <span class="count">(1)</span>', content)  # 1 breakfast in vegetarian
        self.assertIn('Dessert <span class="count">(1)</span>', content)    # 1 dessert in vegetarian
        self.assertIn('Quick <span class="count">(1)</span>', content)      # 1 quick in vegetarian