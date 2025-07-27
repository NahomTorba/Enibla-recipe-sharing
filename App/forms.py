from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Recipe

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    favorite_cuisines = forms.MultipleChoiceField(
        choices=UserProfile.CUISINE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ('bio', 'profile_image', 'favorite_cuisines')

class RecipeForm(forms.ModelForm):
    tags = forms.MultipleChoiceField(
        choices=Recipe.TAG_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Recipe
        fields = (
            'title', 'description', 'ingredients', 'instructions',
            'prep_time', 'cook_time', 'servings', 'image', 'tags'
        )
        widgets = {
            'ingredients': forms.Textarea(attrs={'rows': 4}),
            'instructions': forms.Textarea(attrs={'rows': 6}),
        }
