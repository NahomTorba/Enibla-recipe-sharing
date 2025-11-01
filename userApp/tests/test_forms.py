from django.test import TestCase
from django.contrib.auth.models import User
from userApp.forms import SignUpForm
from userApp.models import UserProfile
from userApp.forms import UserProfileForm

class SignUpFormTest(TestCase):

    def test_form_valid_data(self):
        # Data that should pass validation
        data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }

        form = SignUpForm(data=data)
        self.assertTrue(form.is_valid())  # Check if the form is valid

        # Check if the user is created in the database
        form.save()
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'testuser@example.com')

    def test_username_too_short(self):
        data = {
            'username': 'us',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())  # Check if the form is not valid
        self.assertEqual(form.errors['username'], ['Username must be at least 3 characters long.'])

    def test_username_invalid_characters(self):
        data = {
            'username': 'invalid@user',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())  # Check if the form is not valid
        self.assertEqual(form.errors['username'], ['Username can only contain letters, numbers, and underscores.'])

    def test_email_already_registered(self):
        # Create a user to test the email conflict
        User.objects.create_user(username='existinguser', email='testuser@example.com', password='password123')

        data = {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'testuser@example.com',  # Same email as the existing user
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())  # Check if the form is not valid
        self.assertEqual(form.errors['email'], ['This email address is already registered.'])

    def test_first_name_too_short(self):
        data = {
            'username': 'testuser',
            'first_name': 'J',  # Too short
            'last_name': 'Doe',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())  # Check if the form is not valid
        self.assertEqual(form.errors['first_name'], ['First name must be at least 2 characters long.'])

    def test_last_name_too_short(self):
        data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'D',  # Too short
            'email': 'testuser@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())  # Check if the form is not valid
        self.assertEqual(form.errors['last_name'], ['Last name must be at least 2 characters long.'])

    def test_password_mismatch(self):
        data = {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123!',
            'password2': 'MismatchPassword123!'
        }

        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())  # Check if the form is not valid
        self.assertEqual(form.errors['password2'], ['The two password fields didn’t match.'])

    def test_form_field_widgets(self):
        # Check if the placeholders and classes are set correctly
        form = SignUpForm()

        # Check widget attributes for 'first_name' field
        first_name_widget = form.fields['first_name'].widget.attrs
        self.assertEqual(first_name_widget['placeholder'], 'Enter your first name')
        self.assertEqual(first_name_widget['class'], 'form-control')

        # Check widget attributes for 'email' field
        email_widget = form.fields['email'].widget.attrs
        self.assertEqual(email_widget['placeholder'], 'Enter your email address')
        self.assertEqual(email_widget['class'], 'form-control')

        # Check widget attributes for 'password1' field
        password_widget = form.fields['password1'].widget.attrs
        self.assertEqual(password_widget['placeholder'], 'Create a strong password')
        self.assertEqual(password_widget['class'], 'form-control')
class UserProfileFormTest(TestCase):

    def setUp(self):
        # Create a UserProfile instance for use in tests
        self.user_profile = UserProfile.objects.create(
            profile_image='path/to/image.jpg',
            bio='A passionate cook with a love for spicy foods.',
            favorite_cuisines='Italian,Mexican'
        )

    def test_form_initialization_with_existing_data(self):
        form = UserProfileForm(instance=self.user_profile)
        self.assertEqual(form.initial['favorite_cuisines'], ['Italian', 'Mexican'])

    def test_form_initialization_with_no_data(self):
        user_profile = UserProfile.objects.create(profile_image='path/to/image.jpg', bio='Test bio')
        form = UserProfileForm(instance=user_profile)
        self.assertEqual(form.initial['favorite_cuisines'], [])

    def test_form_save_with_valid_data(self):
        form_data = {
            'profile_image': 'path/to/image.jpg',
            'bio': 'Test bio',
            'favorite_cuisines': ['Italian', 'Mexican']
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())
        profile = form.save()
        self.assertEqual(profile.favorite_cuisines, 'Italian,Mexican')

    def test_form_save_with_no_favorite_cuisines(self):
        form_data = {
            'profile_image': 'path/to/image.jpg',
            'bio': 'Test bio',
            'favorite_cuisines': []
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())
        profile = form.save()
        self.assertEqual(profile.favorite_cuisines, '')

    def test_form_invalid_favorite_cuisines(self):
        form_data = {
            'profile_image': 'path/to/image.jpg',
            'bio': 'Test bio',
            'favorite_cuisines': ['InvalidCuisine']
        }
        form = UserProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('favorite_cuisines', form.errors)

    def test_form_bio_max_length(self):
        form_data = {
            'profile_image': 'path/to/image.jpg',
            'bio': 'a' * 501,  # Exceeds 500 characters
            'favorite_cuisines': ['Italian']
        }
        form = UserProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('bio', form.errors)

    def test_form_rendering(self):
        form = UserProfileForm(instance=self.user_profile)
        self.assertIn('<textarea', form.as_p())
        self.assertIn('<input type="checkbox"', form.as_p())

    def test_form_save_with_bio_only(self):
        form_data = {
            'profile_image': 'path/to/image.jpg',
            'bio': 'A bio without cuisines.',
            'favorite_cuisines': []
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())
        profile = form.save()
        self.assertEqual(profile.favorite_cuisines, '')
        self.assertEqual(profile.bio, 'A bio without cuisines.')
