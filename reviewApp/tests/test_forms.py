from django.test import TestCase
from reviewApp.forms import ReviewForm
from django.forms.models import model_to_dict

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