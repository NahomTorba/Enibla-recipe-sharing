from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from recipeApp.models import Recipe
from userApp.models import UserProfile


class RecipeAppURLsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user and profile
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            favorite_cuisines='Ethiopian,Italian'
        )
        
        # Create test recipe
        self.recipe = Recipe.objects.create(
            author=self.user_profile,
            title='Test Recipe',
            description='A delicious test recipe',
            ingredients='2 cups flour\n1 cup sugar',
            instructions='Mix ingredients and bake',
            tags='breakfast,dessert',
            cuisine='Ethiopian',
            difficulty='Easy',
            prep_time=30
        )

    def test_create_recipe_url_resolves(self):
        """Test that create_recipe URL resolves correctly"""
        url = reverse('create_recipe')
        self.assertEqual(url, '/create/')
        
        # Test URL resolution
        resolved = resolve('/create/')
        self.assertEqual(resolved.view_name, 'create_recipe')

    def test_create_recipe_url_get(self):
        """Test create_recipe URL with GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_create_recipe_url_post(self):
        """Test create_recipe URL with POST request"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': 'New Recipe',
            'description': 'A wonderful new recipe for testing',
            'ingredients': '2 cups flour\n1 cup sugar\n3 eggs',
            'instructions': 'Mix all ingredients together and bake for 30 minutes at 350°F',
            'cuisine': 'Italian',
            'difficulty': 'Medium',
            'prep_time': 45,
        }
        response = self.client.post('/create/', data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

    def test_create_recipe_url_unauthenticated(self):
        """Test create_recipe URL redirects unauthenticated users"""
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_edit_recipe_url_resolves(self):
        """Test that edit_recipe URL resolves correctly"""
        url = reverse('edit_recipe', kwargs={'slug': self.recipe.slug})
        expected_url = f'/{self.recipe.slug}/edit/'
        self.assertEqual(url, expected_url)
        
        # Test URL resolution
        resolved = resolve(expected_url)
        self.assertEqual(resolved.view_name, 'edit_recipe')
        self.assertEqual(resolved.kwargs['slug'], self.recipe.slug)

    def test_edit_recipe_url_get(self):
        """Test edit_recipe URL with GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/{self.recipe.slug}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_edit_recipe_url_post(self):
        """Test edit_recipe URL with POST request"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': 'Updated Recipe',
            'description': 'An updated description for the recipe',
            'ingredients': '3 cups flour\n2 cups sugar\n4 eggs',
            'instructions': 'Updated instructions: Mix all ingredients and bake for 45 minutes',
            'cuisine': 'Mexican',
            'difficulty': 'Hard',
            'prep_time': 60,
        }
        response = self.client.post(f'/{self.recipe.slug}/edit/', data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update

    def test_edit_recipe_url_unauthorized(self):
        """Test edit_recipe URL with unauthorized user"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(f'/{self.recipe.slug}/edit/')
        self.assertEqual(response.status_code, 302)  # Redirect to recipe detail

    def test_edit_recipe_url_not_found(self):
        """Test edit_recipe URL with non-existing recipe"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/non-existent-recipe/edit/')
        self.assertEqual(response.status_code, 302)  # Redirect to index

    def test_delete_recipe_url_resolves(self):
        """Test that delete_recipe URL resolves correctly"""
        url = reverse('delete_recipe', kwargs={'slug': self.recipe.slug})
        expected_url = f'/{self.recipe.slug}/delete/'
        self.assertEqual(url, expected_url)
        
        # Test URL resolution
        resolved = resolve(expected_url)
        self.assertEqual(resolved.view_name, 'delete_recipe')
        self.assertEqual(resolved.kwargs['slug'], self.recipe.slug)

    def test_delete_recipe_url_get(self):
        """Test delete_recipe URL with GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/{self.recipe.slug}/delete/')
        self.assertEqual(response.status_code, 200)

    def test_delete_recipe_url_post(self):
        """Test delete_recipe URL with POST request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/{self.recipe.slug}/delete/')
        self.assertEqual(response.status_code, 302)  # Redirect after deletion

    def test_delete_recipe_url_unauthorized(self):
        """Test delete_recipe URL with unauthorized user"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(f'/{self.recipe.slug}/delete/')
        self.assertEqual(response.status_code, 302)  # Redirect to recipe detail

    def test_delete_recipe_url_not_found(self):
        """Test delete_recipe URL with non-existing recipe"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/non-existent-recipe/delete/')
        self.assertEqual(response.status_code, 302)  # Redirect to index

    def test_recipe_list_url_resolves(self):
        """Test that recipe_list URL resolves correctly"""
        url = reverse('recipe_list')
        self.assertEqual(url, '/recipes/')
        
        # Test URL resolution
        resolved = resolve('/recipes/')
        self.assertEqual(resolved.view_name, 'recipe_list')

    def test_recipe_list_url_get(self):
        """Test recipe_list URL with GET request"""
        response = self.client.get('/recipes/')
        self.assertEqual(response.status_code, 200)

    def test_recipe_list_url_with_query_params(self):
        """Test recipe_list URL with query parameters"""
        response = self.client.get('/recipes/', {
            'q': 'test',
            'cuisine': 'Ethiopian',
            'difficulty': 'Easy',
            'prep_time': '30',
            'tag': 'breakfast',
            'page': '1'
        })
        self.assertEqual(response.status_code, 200)

    def test_recipe_list_url_pagination(self):
        """Test recipe_list URL with pagination"""
        response = self.client.get('/recipes/', {'page': '1'})
        self.assertEqual(response.status_code, 200)

    def test_recipe_list_url_invalid_page(self):
        """Test recipe_list URL with invalid page number"""
        response = self.client.get('/recipes/', {'page': '999'})
        self.assertEqual(response.status_code, 200)  # Should handle gracefully

    def test_recipe_detail_url_resolves(self):
        """Test that recipe_detail URL resolves correctly"""
        url = reverse('recipe_detail', kwargs={'slug': self.recipe.slug})
        expected_url = f'/{self.recipe.slug}/'
        self.assertEqual(url, expected_url)
        
        # Test URL resolution
        resolved = resolve(expected_url)
        self.assertEqual(resolved.view_name, 'recipe_detail')
        self.assertEqual(resolved.kwargs['slug'], self.recipe.slug)

    def test_recipe_detail_url_get(self):
        """Test recipe_detail URL with GET request"""
        response = self.client.get(f'/{self.recipe.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_url_authenticated(self):
        """Test recipe_detail URL with authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/{self.recipe.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_url_not_found(self):
        """Test recipe_detail URL with non-existing recipe"""
        response = self.client.get('/non-existent-recipe/')
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_url_with_special_characters(self):
        """Test recipe_detail URL with special characters in slug"""
        # Create recipe with special characters in title
        special_recipe = Recipe.objects.create(
            author=self.user_profile,
            title='Recipe with Special Characters!',
            description='A recipe with special characters',
            ingredients='2 cups flour',
            instructions='Mix and bake',
            tags='breakfast'
        )
        
        response = self.client.get(f'/{special_recipe.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_url_patterns_order(self):
        """Test that URL patterns are in correct order to avoid conflicts"""
        # Test that more specific patterns come before general ones
        # recipe_detail should come after edit and delete to avoid conflicts
        
        # These should all resolve to different views
        edit_url = f'/{self.recipe.slug}/edit/'
        delete_url = f'/{self.recipe.slug}/delete/'
        detail_url = f'/{self.recipe.slug}/'
        
        # Test that each resolves to the correct view
        edit_resolved = resolve(edit_url)
        delete_resolved = resolve(delete_url)
        detail_resolved = resolve(detail_url)
        
        self.assertEqual(edit_resolved.view_name, 'edit_recipe')
        self.assertEqual(delete_resolved.view_name, 'delete_recipe')
        self.assertEqual(detail_resolved.view_name, 'recipe_detail')

    def test_url_names_consistency(self):
        """Test that URL names are consistent and follow naming conventions"""
        # Test that all URL names follow the expected pattern
        expected_names = [
            'create_recipe',
            'edit_recipe', 
            'delete_recipe',
            'recipe_list',
            'recipe_detail'
        ]
        
        for name in expected_names:
            try:
                reverse(name)
            except Exception as e:
                self.fail(f"URL name '{name}' is not valid: {e}")

    def test_slug_parameter_validation(self):
        """Test that slug parameters are properly handled"""
        # Test with valid slug
        response = self.client.get(f'/{self.recipe.slug}/')
        self.assertEqual(response.status_code, 200)
        
        # Test with invalid slug format (should still try to resolve)
        response = self.client.get('/invalid-slug-format/')
        self.assertEqual(response.status_code, 404)

    def test_url_trailing_slashes(self):
        """Test URL handling with and without trailing slashes"""
        # Test with trailing slash
        response = self.client.get('/recipes/')
        self.assertEqual(response.status_code, 200)
        
        # Test without trailing slash (should redirect)
        response = self.client.get('/recipes')
        self.assertEqual(response.status_code, 301)  # Permanent redirect

    def test_recipe_detail_url_case_sensitivity(self):
        """Test that recipe detail URL is case sensitive for slug"""
        # Create recipe with uppercase in slug
        uppercase_recipe = Recipe.objects.create(
            author=self.user_profile,
            title='UPPERCASE Recipe',
            description='A recipe with uppercase',
            ingredients='2 cups flour',
            instructions='Mix and bake',
            tags='breakfast'
        )
        
        # Test exact slug match
        response = self.client.get(f'/{uppercase_recipe.slug}/')
        self.assertEqual(response.status_code, 200)
        
        # Test case-sensitive slug
        response = self.client.get(f'/{uppercase_recipe.slug.lower()}/')
        self.assertEqual(response.status_code, 404)

    def test_url_parameters_preservation(self):
        """Test that URL parameters are preserved in redirects"""
        # Test create recipe redirect preserves parameters
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/create/?next=/recipes/')
        self.assertEqual(response.status_code, 200)

    def test_recipe_list_url_with_filters(self):
        """Test recipe_list URL with various filter combinations"""
        filter_combinations = [
            {'q': 'test'},
            {'cuisine': 'Ethiopian'},
            {'difficulty': 'Easy'},
            {'prep_time': '30'},
            {'tag': 'breakfast'},
            {'q': 'test', 'cuisine': 'Ethiopian'},
            {'cuisine': 'Ethiopian', 'difficulty': 'Easy', 'prep_time': '30'},
            {'tag': ['breakfast', 'dessert']},
        ]
        
        for filters in filter_combinations:
            response = self.client.get('/recipes/', filters)
            self.assertEqual(response.status_code, 200, f"Failed with filters: {filters}")

    def test_recipe_urls_with_unicode_slugs(self):
        """Test recipe URLs with unicode characters in slugs"""
        # Create recipe with unicode characters
        unicode_recipe = Recipe.objects.create(
            author=self.user_profile,
            title='Recipe with Üñíçødé',
            description='A recipe with unicode characters',
            ingredients='2 cups flour',
            instructions='Mix and bake',
            tags='breakfast'
        )
        
        response = self.client.get(f'/{unicode_recipe.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_url_reverse_lookup_consistency(self):
        """Test that reverse lookup works consistently for all URLs"""
        # Test all URL reverse lookups
        create_url = reverse('create_recipe')
        list_url = reverse('recipe_list')
        detail_url = reverse('recipe_detail', kwargs={'slug': self.recipe.slug})
        edit_url = reverse('edit_recipe', kwargs={'slug': self.recipe.slug})
        delete_url = reverse('delete_recipe', kwargs={'slug': self.recipe.slug})
        
        # Verify all URLs are strings and not empty
        self.assertIsInstance(create_url, str)
        self.assertIsInstance(list_url, str)
        self.assertIsInstance(detail_url, str)
        self.assertIsInstance(edit_url, str)
        self.assertIsInstance(delete_url, str)
        
        self.assertTrue(len(create_url) > 0)
        self.assertTrue(len(list_url) > 0)
        self.assertTrue(len(detail_url) > 0)
        self.assertTrue(len(edit_url) > 0)
        self.assertTrue(len(delete_url) > 0)

    def test_url_pattern_conflicts(self):
        """Test that URL patterns don't conflict with each other"""
        # Test that different URL patterns resolve to different views
        patterns_to_test = [
            ('/create/', 'create_recipe'),
            ('/recipes/', 'recipe_list'),
            (f'/{self.recipe.slug}/', 'recipe_detail'),
            (f'/{self.recipe.slug}/edit/', 'edit_recipe'),
            (f'/{self.recipe.slug}/delete/', 'delete_recipe'),
        ]
        
        for url, expected_view in patterns_to_test:
            resolved = resolve(url)
            self.assertEqual(resolved.view_name, expected_view, 
                           f"URL {url} should resolve to {expected_view}")

    def test_url_http_methods(self):
        """Test that URLs handle appropriate HTTP methods"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test GET methods
        get_urls = [
            '/create/',
            '/recipes/',
            f'/{self.recipe.slug}/',
            f'/{self.recipe.slug}/edit/',
            f'/{self.recipe.slug}/delete/',
        ]
        
        for url in get_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302, 404], 
                         f"GET {url} returned unexpected status: {response.status_code}")
        
        # Test POST methods where applicable
        post_urls = [
            ('/create/', {'title': 'Test', 'description': 'Test description', 
                         'ingredients': 'Test ingredients', 'instructions': 'Test instructions'}),
            (f'/{self.recipe.slug}/edit/', {'title': 'Updated', 'description': 'Updated description',
                                          'ingredients': 'Updated ingredients', 'instructions': 'Updated instructions'}),
            (f'/{self.recipe.slug}/delete/', {}),
        ]
        
        for url, data in post_urls:
            response = self.client.post(url, data)
            self.assertIn(response.status_code, [200, 302, 404], 
                         f"POST {url} returned unexpected status: {response.status_code}")


