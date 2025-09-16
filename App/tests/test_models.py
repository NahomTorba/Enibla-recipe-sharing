from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.urls import reverse
from App.models import UserProfile, Recipe, slugify
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()

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

class RecipeDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserProfile.objects.create(username='testuser', bio='Passionate chef')

        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Spicy Lentil Stew",
            slug= slugify ("Spicy Lentil Stew"),
            description="Ethiopian-inspired lentils with berbere spice.",
            ingredients="1 cup lentils, berbere, onion, garlic",
            instructions="Simmer lentils with spices for 45 minutes.",
            tags="dinner",
            image=SimpleUploadedFile(name='lentils.jpg', content=b'image_bytes', content_type='image/jpeg'),
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

    def test_detail_view_status_code(self):
        url = reverse('recipe_detail', kwargs={'slug': self.recipe.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_view_template(self):
        url = reverse('recipe_detail', kwargs={'slug': self.recipe.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'your_app/recipe_detail.html')  # adjust as needed

    def test_layout_contains_key_fields(self):
        url = reverse('recipe_detail', kwargs={'slug': self.recipe.slug})
        response = self.client.get(url)

        self.assertContains(response, self.recipe.title)
        self.assertContains(response, self.recipe.description)
        self.assertContains(response, self.recipe.ingredients)
        self.assertContains(response, self.recipe.instructions)
        self.assertContains(response, "Dinner")  # assuming you're rendering the tag nicely

    def test_image_display_on_page(self):
        url = reverse('recipe_detail', kwargs={'slug': self.recipe.slug})
        response = self.client.get(url)
        self.assertContains(response, 'recipe_images/lentils.jpg')

    def test_404_for_missing_recipe(self):
        url = reverse('recipe_detail', kwargs={'slug': 'non-existent-slug'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

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