from django.test import TestCase
from django.contrib.auth.models import User
from recipeApp.models import UserProfile
from django.utils import timezone

class UserProfileModelTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_user_profile_creation(self):
        profile = UserProfile.objects.create(
            user=self.user,
            username='testuser',
            bio='Just a test user.',
            favorite_cuisines='Ethiopian,Italian',
        )

        self.assertEqual(profile.user.username, 'testuser')
        self.assertEqual(profile.username, 'testuser')
        self.assertEqual(profile.bio, 'Just a test user.')
        self.assertEqual(profile.favorite_cuisines, 'Ethiopian,Italian')
        self.assertTrue(isinstance(profile.created_at, timezone.datetime))
        self.assertTrue(isinstance(profile.updated_at, timezone.datetime))

    def test_str_method(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), "testuser's Profile")

    def test_get_favorite_cuisines_list(self):
        profile = UserProfile.objects.create(
            user=self.user,
            favorite_cuisines='Ethiopian,Italian,Mexican'
        )
        expected_list = ['Ethiopian', 'Italian', 'Mexican']
        self.assertEqual(profile.get_favorite_cuisines_list(), expected_list)

    def test_get_favorite_cuisines_list_empty(self):
        profile = UserProfile.objects.create(user=self.user, favorite_cuisines='')
        self.assertEqual(profile.get_favorite_cuisines_list(), [])

    def test_profile_image_optional(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertIsNone(profile.profile_image)
