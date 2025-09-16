from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class SignUpForm(UserCreationForm):
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
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a unique username',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a strong password',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'class': 'form-control'
        })

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        if not username.replace('_', '').isalnum():
            raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if len(first_name) < 2:
            raise forms.ValidationError("First name must be at least 2 characters long.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if len(last_name) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters long.")
        return last_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
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
        if self.instance and self.instance.favorite_cuisines:
            self.fields['favorite_cuisines'].initial = self.instance.get_favorite_cuisines_list()

    def save(self, commit=True):
        profile = super().save(commit=False)

        #store favorite cuisines as a comma-separated string
        cuisines = self.cleaned_data.get('favorite_cuisines')
        profile.favorite_cuisines = ','.join(cuisines) if cuisines else ''

        if commit:
            profile.save()
        return profile
