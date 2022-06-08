from urllib import response
from django.test import TestCase


class ViewTestClass(TestCase):
    def test_404_page_not_found(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
    
    # def test_403_permission_denied_view(self):
    #     response = self.client.get()
