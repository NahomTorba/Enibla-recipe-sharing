from django import forms
from App.models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your thoughts about this recipe...',
                'class': 'form-control'
            })
        }
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating or rating < 1 or rating > 5:
            raise forms.ValidationError('Please select a rating between 1 and 5 stars.')
        return rating
