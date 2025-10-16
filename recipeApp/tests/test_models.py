from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from userApp.models import UserProfile
from recipeApp.models import Recipe
from django.contrib.auth.models import User
from PIL import Image
import io


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
        expected = ['dinner', 'Italian']
        self.assertEqual(self.recipe.get_tag_choices_list, expected)

    def test_recipe_image_upload(self):
        """Test image upload handling in the Recipe model."""

         # Create a valid in-memory image
        img = Image.new('RGB', (1000, 1000), color='red')  # Over 800px to trigger resizing
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)

        image_data = SimpleUploadedFile("test.jpg", b"fake_image_data", content_type="image/jpeg")
        recipe_with_image = Recipe.objects.create(
            author=self.profile,
            title='Recipe with Image',
            slug='recipe-with-image',
            description='Testing image upload functionality.',
            ingredients='Ingredients list',
            instructions='Instructions here',
            tags='breakfast',
            image=image_data,
            cuisine='Italian',         
            difficulty='Easy',    
            prep_time=20,       
        )
        self.assertTrue(recipe_with_image.image)

        #testing resize functionality
        recipe_with_image.image.open()
        resized_img = Image.open(recipe_with_image.image)
        self.assertLessEqual(resized_img.width, 800)
        self.assertLessEqual(resized_img.height, 800)
