from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from http import HTTPStatus

User = get_user_model()


class UserUrlTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='darth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_users_urls_uses_correct_template(self):
        """Url-адрес приложения users использует соотвествующий шаблон"""
        templates_url_names = {
            'users/signup.html': '/auth/signup/',
            'users/logged_out.html': '/auth/logout/',
            'users/login.html': '/auth/login/',
            'users/password_change_form.html': '/auth/password_change/',
            'users/password_change_done.html': '/auth/password_change/done/',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/',
            'users/password_reset_confirm.html':
            '/auth/reset/<uidb64>/<token>/',
            'users/password_reset_complete.html': '/auth/reset/done/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                self.authorized_client.force_login(self.user)
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_users_publicly_avaliable_pages(self):
        """Проверяет страницы в публичном доступе."""
        urls_responses = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            # '/auth/reset/done': HTTPStatus.OK,
        }
        for url, expected_value in urls_responses.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_value)

    def test_users_pages_avaliable_to_authorized(self):
        """Проверяет страницы, доступные авторизованному пользователю."""
        urls_responses = {
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_change/done/': HTTPStatus.OK,
        }
        for url, expected_value in urls_responses.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_value)

    def test_password_change_redirects_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя
        на страницу авторизации"""
        response = self.guest_client.get('/auth/password_change/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/auth/password_change/')
        )
