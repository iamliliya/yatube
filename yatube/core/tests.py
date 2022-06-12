from django.test import TestCase

from http import HTTPStatus


class ViewTestClass(TestCase):
    def test_404_page_not_found(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
