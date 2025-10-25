from django.test import TestCase
from django.contrib.auth.models import User
from reviewApp.models import Review, Recipe

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
