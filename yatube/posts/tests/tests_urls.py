from django.test import TestCase, Client

from http import HTTPStatus

from ..models import Group, Post, User


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='darth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group,
        )

    def test_publicly_avaliable_pages(self):
        """Проверка общедоступных страниц"""
        urls_responses = {
            '/': HTTPStatus.OK,
            '/group/test_slug/': HTTPStatus.OK,
            '/profile/darth/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, expected_value in urls_responses.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_value)

    def test_create_exists_at_desired_location_authorised(self):
        """Страница /create/ доступна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя
        на страницу авторизации"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/')
        )

    def test_post_edit_available_to_author(self):
        """Страница /post/edit/ доступна автору поста"""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.authorized_client == self.post.author
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_redirects_non_author(self):
        """Страница /post/edit/ перенаправляет нe автора поста
        на страницу с подробной информацией о посте"""
        self.user2 = User.objects.create(username='obiwan')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        response = self.authorized_client2.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_urls_uses_corrrect_template(self):
        """Url-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/darth/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create.html',
            '/create/': 'posts/create.html',
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
