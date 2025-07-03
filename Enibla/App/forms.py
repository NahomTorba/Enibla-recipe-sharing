from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile,Recipe, Review  

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


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Give your recipe a catchy name',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your recipe, what makes it special, or share the story behind it...',
                'maxlength': '500',
                'rows': 4,
                'class': 'form-control'
            }),
            'ingredients': forms.Textarea(attrs={
                'placeholder': 'List each ingredient on a new line:\n• 2 cups all-purpose flour\n• 1 tsp baking powder\n• 1/2 cup sugar\n• 2 large eggs',
                'rows': 8,
                'class': 'form-control'
            }),
            'instructions': forms.Textarea(attrs={
                'placeholder': 'Write clear, step-by-step instructions:\n1. Preheat oven to 350°F (175°C)\n2. In a large bowl, mix flour and baking powder\n3. In another bowl, cream butter and sugar...',
                'rows': 10,
                'class': 'form-control'
            }),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 3:
            raise forms.ValidationError("Recipe title must be at least 3 characters long.")
        return title

    def clean_description(self):
        description = self.cleaned_data['description']
        if len(description) < 10:
            raise forms.ValidationError("Recipe description must be at least 10 characters long.")
        return description

    def clean_ingredients(self):
        ingredients = self.cleaned_data['ingredients']
        if len(ingredients.strip()) < 10:
            raise forms.ValidationError("Please provide a detailed list of ingredients.")
        return ingredients

    def clean_instructions(self):
        instructions = self.cleaned_data['instructions']
        if len(instructions.strip()) < 20:
            raise forms.ValidationError("Please provide detailed cooking instructions.")
        return instructions

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
