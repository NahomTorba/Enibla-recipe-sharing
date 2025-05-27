from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name',
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name',
            'class': 'form-control'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a unique username',
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        })
    )
    favorite_cuisines = forms.MultipleChoiceField(
        choices=UserProfile.CUISINE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = UserProfile
        fields = ['profile_image', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'placeholder': 'Tell us about your culinary journey, favorite cooking memories, or what you love about food...',
                'maxlength': '500',
                'rows': 5,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email

        if isinstance and self.instance.favorite_cuisines:
            self.fields['favorite_cuisines'].initial = self.instance.get_favorite_cuisines_list()

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update User model fields
        if profile.user:
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.username = self.cleaned_data['username']
            profile.user.email = self.cleaned_data['email']
            if commit:
                profile.user.save()
        
        if commit:
            profile.save()
        return profile

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.instance and self.instance.user:
            # If editing existing profile, exclude current user from uniqueness check
            if User.objects.filter(username=username).exclude(id=self.instance.user.id).exists():
                raise forms.ValidationError("This username is already taken.")
        else:
            # If creating new profile
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.instance and self.instance.user:
            # If editing existing profile, exclude current user from uniqueness check
            if User.objects.filter(email=email).exclude(id=self.instance.user.id).exists():
                raise forms.ValidationError("This email is already registered.")
        else:
            # If creating new profile
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("This email is already registered.")
        return email
