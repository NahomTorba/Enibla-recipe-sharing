from django import forms

from django import forms
from .models import Recipe


class RecipeForm(forms.ModelForm):
    cuisine = forms.ChoiceField(
        choices=Recipe.CUISINE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    difficulty = forms.ChoiceField(
        choices=Recipe.DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    prep_time = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preparation time (minutes)'})
    )
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 'image', 'cuisine', 'difficulty', 'prep_time']
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

    def clean(self):
        cleaned_data = super().clean()
        cuisine = cleaned_data.get('cuisine')
        difficulty = cleaned_data.get('difficulty')
        prep_time = cleaned_data.get('prep_time')
        if cuisine == '':
            cleaned_data['cuisine'] = None
        if difficulty == '':
            cleaned_data['difficulty'] = None
        if prep_time in [None, '']:
            cleaned_data['prep_time'] = None
        return cleaned_data

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
