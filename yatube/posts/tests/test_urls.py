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
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.post.author}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, expected_value in urls_responses.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_value)

    def test_pages_avaliable_to_authorized_user(self):
        """Проверка страниц, доступных авторизованному пользователю"""
        urls_responses = {
            '/create/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
        }
        for url, expected_value in urls_responses.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_value)

    def test_create_url_redirect_anonymous(self):
        """Страницы перенаправляет анонимного
        пользователя на страницу авторизации"""
        urls_redirects = {
            '/create/': '/auth/login/?next=/create/',
            '/follow/': '/auth/login/?next=/follow/',
            f'/profile/{self.user}/follow/':
            f'/auth/login/?next=/profile/{self.user}/follow/',
            f'/profile/{self.user}/unfollow/':
            f'/auth/login/?next=/profile/{self.user}/unfollow/',
        }
        for url, expected_redirect in urls_redirects.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, expected_redirect)

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
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create.html',
            '/create/': 'posts/create.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
