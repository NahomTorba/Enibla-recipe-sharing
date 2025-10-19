from django.urls import reverse
from django.test import TestCase
from django.conf import settings

class TestURLs(TestCase):
    
    def test_home_url(self):
        """Test if the home URL resolves correctly"""
        url = reverse('home')  # Using reverse to dynamically resolve the URL by name
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'home.html') 
    
    def test_index_url(self):
        """Test if the index URL resolves correctly"""
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')  

    def test_media_url_in_debug_mode(self):
        """Test if media URL is correctly handled when DEBUG is True"""
        if settings.DEBUG:
            url = reverse('home')  # or reverse('index')
            response = self.client.get(url)
            # Test that media URLs are served correctly when DEBUG is True
            self.assertContains(response, settings.MEDIA_URL)  # Check if MEDIA_URL is present in the response
