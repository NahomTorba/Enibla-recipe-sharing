from django.test import TestCase
from reviewApp.forms import ReviewForm
from django.forms import HiddenInput

class ReviewFormTest(TestCase):
    def test_valid_form_submission(self):
        # Valid data
        data = {
            'rating': 4,
            'comment': 'Great recipe, will try it!'
        }
        
        form = ReviewForm(data=data)
        
        # Check form is valid
        self.assertTrue(form.is_valid())
        
        # Check cleaned data
        cleaned_data = form.cleaned_data
        self.assertEqual(cleaned_data['rating'], 4)
        self.assertEqual(cleaned_data['comment'], 'Great recipe, will try it!')

    def test_invalid_rating_too_low(self):
            # Invalid rating (less than 1)
            data = {
                'rating': 0,
                'comment': 'This is a bad recipe.'
            }
            
            form = ReviewForm(data=data)
            
            # Check form is invalid
            self.assertFalse(form.is_valid())
            
            # Check error message for rating
            self.assertEqual(form.errors['rating'], ['Please select a rating between 1 and 5 stars.'])

    def test_invalid_rating_too_high(self):
            # Invalid rating (more than 5)
            data = {
                'rating': 6,
                'comment': 'This is a bad recipe.'
            }
            
            form = ReviewForm(data=data)
            
            # Check form is invalid
            self.assertFalse(form.is_valid())
            
            # Check error message for rating
            self.assertEqual(form.errors['rating'], ['Please select a rating between 1 and 5 stars.'])

    def test_missing_rating(self):
        # Missing rating field
        data = {
            'comment': 'It was okay.'
        }
        
        form = ReviewForm(data=data)
        
        # Check form is invalid
        self.assertFalse(form.is_valid())
        
        # Check error message for rating
        self.assertEqual(form.errors['rating'], ['This field is required.'])

    def test_empty_comment(self):
        # Valid rating, but empty comment
        data = {
            'rating': 5,
            'comment': ''
        }
        
        form = ReviewForm(data=data)
        
        # Check form is valid (since comment is not a required field)
        self.assertTrue(form.is_valid())
        
        # Check cleaned data
        cleaned_data = form.cleaned_data
        self.assertEqual(cleaned_data['rating'], 5)
        self.assertEqual(cleaned_data['comment'], '')

    def test_large_comment(self):
        # A very large comment
        large_comment = 'a' * 1000  # Create a long comment string
        
        data = {
            'rating': 5,
            'comment': large_comment
        }
        
        form = ReviewForm(data=data)
        
        # Check form is valid
        self.assertTrue(form.is_valid())
        
        # Check cleaned data
        cleaned_data = form.cleaned_data
        self.assertEqual(cleaned_data['rating'], 5)
        self.assertEqual(cleaned_data['comment'], large_comment)

    def test_hidden_rating_field(self):
        # Create the form
        form = ReviewForm()
        
        # Check if 'rating' is rendered as a hidden input
        rating_widget = form.fields['rating'].widget
        self.assertIsInstance(rating_widget, HiddenInput)

    def test_empty_form_submission(self):
        # Empty data
        data = {}
        
        form = ReviewForm(data=data)
        
        # Check form is invalid
        self.assertFalse(form.is_valid())
        
        # Check error messages
        self.assertEqual(form.errors['rating'], ['This field is required.'])
        self.assertEqual(form.errors['comment'], ['This field is required.'])