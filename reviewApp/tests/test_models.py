from django.test import TestCase
from django.contrib.auth.models import User
from reviewApp.models import Review, SavedRecipe
from recipeApp.models import Recipe

class ReviewModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.recipe = Recipe.objects.create(title="Test Recipe", description="Test Description")

    def test_create_valid_review(self):
        review = Review.objects.create(
            recipe=self.recipe,
            user=self.user,
            rating=4,
            comment="Great recipe!"
        )
        self.assertEqual(review.recipe, self.recipe)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, "Great recipe!")
        self.assertTrue(review.created_at)

    def test_rating_constraints(self):
        # Test invalid low rating (should raise a validation error)
        with self.assertRaises(ValueError):
            Review.objects.create(
                recipe=self.recipe,
                user=self.user,
                rating=0,  # Below the minimum allowed rating
                comment="Invalid rating"
            )

        # Test invalid high rating (should raise a validation error)
        with self.assertRaises(ValueError):
            Review.objects.create(
                recipe=self.recipe,
                user=self.user,
                rating=6,  # Above the maximum allowed rating
                comment="Invalid rating"
            )

    def test_unique_recipe_user_constraint(self):
        # Create a valid review
        Review.objects.create(
            recipe=self.recipe,
            user=self.user,
            rating=4,
            comment="Great recipe!"
        )
        
        # Try to create another review by the same user for the same recipe
        with self.assertRaises(Exception):
            Review.objects.create(
                recipe=self.recipe,
                user=self.user,
                rating=5,
                comment="Another review"
            )

    def test_review_ordering(self):
        review1 = Review.objects.create(
            recipe=self.recipe,
            user=self.user,
            rating=4,
            comment="Great recipe!"
        )
        review2 = Review.objects.create(
            recipe=self.recipe,
            user=self.user,
            rating=3,
            comment="It's okay"
        )

        # Check if reviews are ordered by created_at in descending order
        reviews = Review.objects.all()
        self.assertEqual(reviews[0], review1)
        self.assertEqual(reviews[1], review2)

class SavedRecipeModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.recipe = Recipe.objects.create(title="Test Recipe", description="Test Description")

    def test_create_valid_saved_recipe(self):
        saved_recipe = SavedRecipe.objects.create(
            user=self.user,
            recipe=self.recipe
        )
        self.assertEqual(saved_recipe.user, self.user)
        self.assertEqual(saved_recipe.recipe, self.recipe)
        self.assertTrue(saved_recipe.saved_at)

    def test_unique_user_recipe_constraint(self):
        # Save the recipe for the user
        SavedRecipe.objects.create(user=self.user, recipe=self.recipe)

        # Try to save the same recipe for the same user again
        with self.assertRaises(Exception):
            SavedRecipe.objects.create(user=self.user, recipe=self.recipe)

    def test_saved_recipe_ordering(self):
        saved_recipe1 = SavedRecipe.objects.create(user=self.user, recipe=self.recipe)
        saved_recipe2 = SavedRecipe.objects.create(user=self.user, recipe=self.recipe)

        # Check if saved recipes are ordered by saved_at in descending order
        saved_recipes = SavedRecipe.objects.all()
        self.assertEqual(saved_recipes[0], saved_recipe2)
        self.assertEqual(saved_recipes[1], saved_recipe1)
