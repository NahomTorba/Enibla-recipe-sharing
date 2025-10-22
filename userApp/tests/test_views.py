from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from unittest.mock import patch, MagicMock
from userApp.models import UserProfile
from userApp.forms import SignUpForm, UserProfileForm


class UserAppViewsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            favorite_cuisines='Ethiopian,Italian'
        )

    def test_signup_view_get(self):
        """Test signup view GET request"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIsInstance(response.context['form'], SignUpForm)

    def test_signup_view_post_valid(self):
        """Test signup view with valid POST data"""
        with patch('userApp.views.send_confirmation_email') as mock_send_email:
            data = {
                'username': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password1': 'newpass123',
                'password2': 'newpass123'
            }
            response = self.client.post(reverse('signup'), data)
            
            # Check user was created
            self.assertTrue(User.objects.filter(username='newuser').exists())
            
            # Check email was sent
            mock_send_email.assert_called_once()
            
            # Check redirect
            self.assertRedirects(response, reverse('index'))

    def test_signup_view_post_invalid(self):
        """Test signup view with invalid POST data"""
        data = {
            'username': 'ab',  # Too short
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',
            'password1': 'pass',
            'password2': 'pass'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_signup_view_authenticated_user(self):
        """Test signup view when user is already authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('signup'))
        self.assertRedirects(response, reverse('index'))

    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_login_view_post_valid(self):
        """Test login view with valid credentials"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertRedirects(response, reverse('index'))

    def test_login_view_post_invalid(self):
        """Test login view with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Invalid username or password' in str(message) for message in messages))

    def test_login_view_authenticated_user(self):
        """Test login view when user is already authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('index'))

    def test_logout_view_authenticated(self):
        """Test logout view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        
        # Check user is logged out
        response = self.client.get(reverse('profile_detail', kwargs={'username': 'testuser'}))
        self.assertRedirects(response, reverse('login'))

    def test_logout_view_unauthenticated(self):
        """Test logout view for unauthenticated user"""
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_profile_create_get(self):
        """Test profile create view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('create_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_profile_create_post_valid(self):
        """Test profile create view with valid POST data"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a simple image file for testing
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )
        
        data = {
            'bio': 'Updated bio',
            'favorite_cuisines': ['Ethiopian', 'Mexican'],
            'profile_image': image
        }
        response = self.client.post(reverse('create_profile'), data)
        self.assertRedirects(response, reverse('profile_detail', kwargs={'username': 'testuser'}))

    def test_profile_create_post_invalid(self):
        """Test profile create view with invalid POST data"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test with invalid image extension
        invalid_image = SimpleUploadedFile(
            "test_image.txt",
            b"fake_content",
            content_type="text/plain"
        )
        
        data = {
            'bio': 'Updated bio',
            'favorite_cuisines': ['Ethiopian', 'Mexican'],
            'profile_image': invalid_image
        }
        response = self.client.post(reverse('create_profile'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Please correct the errors' in str(message) for message in messages))

    def test_profile_create_unauthenticated(self):
        """Test profile create view for unauthenticated user"""
        response = self.client.get(reverse('create_profile'))
        self.assertRedirects(response, reverse('login'))

    def test_profile_detail_existing_profile(self):
        """Test profile detail view for existing profile"""
        response = self.client.get(reverse('profile_detail', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
        self.assertContains(response, 'Test bio')

    def test_profile_detail_non_existing_profile(self):
        """Test profile detail view for non-existing profile"""
        response = self.client.get(reverse('profile_detail', kwargs={'username': 'nonexistent'}))
        self.assertRedirects(response, reverse('home'))

    def test_profile_detail_authenticated_own_profile(self):
        """Test profile detail view for authenticated user viewing own profile"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile_detail', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('saved_recipes', response.context)

    def test_my_profile_authenticated_with_profile(self):
        """Test my_profile view for authenticated user with profile"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_profile'))
        self.assertRedirects(response, reverse('profile_detail', kwargs={'username': 'testuser'}))

    def test_my_profile_authenticated_without_profile(self):
        """Test my_profile view for authenticated user without profile"""
        # Create user without profile
        user_no_profile = User.objects.create_user(
            username='noprofile',
            email='noprofile@example.com',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        response = self.client.get(reverse('my_profile'))
        self.assertRedirects(response, reverse('create_profile'))

    def test_my_profile_unauthenticated(self):
        """Test my_profile view for unauthenticated user"""
        response = self.client.get(reverse('my_profile'))
        self.assertRedirects(response, reverse('login'))

    def test_edit_profile_get(self):
        """Test edit profile view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_edit_profile_post_valid(self):
        """Test edit profile view with valid POST data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'bio': 'Updated bio content',
            'favorite_cuisines': ['Chinese', 'Japanese']
        }
        response = self.client.post(reverse('edit_profile'), data)
        self.assertRedirects(response, reverse('profile_detail', kwargs={'username': 'testuser'}))
        
        # Check profile was updated
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.bio, 'Updated bio content')
        self.assertEqual(updated_profile.favorite_cuisines, 'Chinese,Japanese')

    def test_edit_profile_post_invalid(self):
        """Test edit profile view with invalid POST data"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test with invalid image
        invalid_image = SimpleUploadedFile(
            "test_image.txt",
            b"fake_content",
            content_type="text/plain"
        )
        
        data = {
            'bio': 'Updated bio',
            'profile_image': invalid_image
        }
        response = self.client.post(reverse('edit_profile'), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Please correct the errors' in str(message) for message in messages))

    def test_edit_profile_unauthenticated(self):
        """Test edit profile view for unauthenticated user"""
        response = self.client.get(reverse('edit_profile'))
        self.assertRedirects(response, reverse('login'))

    def test_edit_profile_no_profile_exists(self):
        """Test edit profile view when user has no profile"""
        user_no_profile = User.objects.create_user(
            username='noprofile',
            email='noprofile@example.com',
            password='testpass123'
        )
        self.client.login(username='noprofile', password='testpass123')
        response = self.client.get(reverse('edit_profile'))
        self.assertRedirects(response, reverse('create_profile'))

    def test_edit_profile_remove_image(self):
        """Test edit profile view with image removal"""
        self.client.login(username='testuser', password='testpass123')
        
        # First add an image
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )
        self.user_profile.profile_image = image
        self.user_profile.save()
        
        # Then remove it
        data = {
            'bio': 'Updated bio',
            'remove_image': 'on'
        }
        response = self.client.post(reverse('edit_profile'), data)
        self.assertRedirects(response, reverse('profile_detail', kwargs={'username': 'testuser'}))
        
        # Check image was removed
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertFalse(updated_profile.profile_image)

    def test_login_view_with_next_parameter(self):
        """Test login view with next parameter"""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'next': reverse('profile_detail', kwargs={'username': 'testuser'})
        }
        response = self.client.post(reverse('login'), data)
        self.assertRedirects(response, reverse('profile_detail', kwargs={'username': 'testuser'}))

    def test_signup_view_duplicate_email(self):
        """Test signup view with duplicate email"""
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'test@example.com',  # Same as existing user
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_signup_view_duplicate_username(self):
        """Test signup view with duplicate username"""
        data = {
            'username': 'testuser',  # Same as existing user
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
