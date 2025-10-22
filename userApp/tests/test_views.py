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
