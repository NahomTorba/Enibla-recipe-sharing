from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
from userApp.models import UserProfile
from recipeApp.models import Recipe
from reviewApp.models import Review, SavedRecipe
from random import choice, randint

class Command(BaseCommand):
    help = 'Populate the database with fake data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create fake users and user profiles
        num_users = 10  # 10 users for testing
        for _ in range(num_users):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='Password@123',
            )

            # Create UserProfile for each user
            UserProfile.objects.create(
                user=user,
                bio=fake.text(max_nb_chars=500),
                favorite_cuisines=fake.word() + ',' + fake.word(),  # You can adjust this for more cuisines
                profile_image=None,  # Set a path to a dummy image if you have one
                created_at=fake.date_this_year(),
                updated_at=fake.date_this_year()
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_users} users and profiles.'))

        # Create fake recipes
        num_recipes = 30  # Adjust this number as needed
        for _ in range(num_recipes):
            # Randomly pick an existing UserProfile (author)
            author = choice(UserProfile.objects.all())

            recipe = Recipe.objects.create(
                author=author,
                title=fake.sentence(nb_words=5),
                slug=fake.slug(),
                description=fake.text(),
                ingredients=fake.text(),
                instructions=fake.text(),
                tags=choice([choice(Recipe.TAG_CHOICES)[0] for _ in range(6)]),  # Random tags
                cuisine=choice([choice(Recipe.CUISINE_CHOICES)[0] for _ in range(15)]),  # Random cuisine
                difficulty=choice([difficulty[0] for difficulty in Recipe.DIFFICULTY_CHOICES]),
                prep_time=randint(10, 120),
                created_at=fake.date_this_year(),
                updated_at=fake.date_this_year()
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_recipes} recipes.'))

        # Create fake reviews for recipes
        num_reviews = 50  # Adjust this number as needed
        for _ in range(num_reviews):
            recipe = choice(Recipe.objects.all())
            user = choice(User.objects.all())

            if not Review.objects.filter(user=user, recipe=recipe).exists():
                Review.objects.create(
                    recipe=recipe,
                    user=user,
                    rating=randint(1, 5),
                    comment=fake.text(),
                    created_at=fake.date_this_year()
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_reviews} reviews.'))

        # Create fake saved recipes
        num_saved_recipes = 40  # Adjust this number as needed
        for _ in range(num_saved_recipes):
            user = choice(User.objects.all())
            recipe = choice(Recipe.objects.all())

            if not SavedRecipe.objects.filter(user=user, recipe=recipe).exists():
                    SavedRecipe.objects.create(
                    user=user,
                    recipe=recipe,
                    saved_at=fake.date_this_year()
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_saved_recipes} saved recipes.'))
