from cgitb import html
import shutil
import tempfile
from urllib import request

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post, User, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
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
            description='Test description'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Test comment',
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}): (
                'posts/group_list.html'),
            reverse('posts:profile', kwargs={'username': 'darth'}): (
                'posts/profile.html'
            ),
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): ('posts/post_detail.html'),
            reverse('posts:post_create'): ('posts/create.html'),
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        self.assertIn('page_obj', response.context)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    def test_group_page_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'})
        )
        post = response.context['page_obj'][0]
        group = response.context['group']
        self.assertIn('page_obj', response.context)
        self.assertEqual(group, self.group)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image, self.post.image)

    def test_profile_shows_correct_context(self):
        """Шаблон posts/profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'darth'})
        )
        post = response.context['page_obj'][0]
        author = response.context['author']
        self.assertIn('page_obj', response.context)
        self.assertIn('following', response.context)
        self.assertEqual(author, self.user)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, self.post.image)

    def test_post_detail_shows_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post = response.context['post']
        comment = response.context['comments'][0]
        self.assertIn('post', response.context)
        self.assertIn('comments', response.context)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, self.post.image)
        self.assertEqual(comment, self.comment)


    def test_post_create_shows_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_creates_post(self):
        response = self.authorized_client.get(reverse('posts:index'))
        count1 = len(response.context['page_obj'])
        Post.objects.create(
            text='Test text 2',
            group=self.group,
            author=self.user,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        count2 = len(response.context['page_obj'])
        self.assertEqual(count2, count1 + 1)

    def test_edit_shows_correct_template(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['post_id'], self.post.id)
        self.assertEqual(response.context['is_edit'], True)

    def test_post_with_group_shows_on_correct_pages(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertIn(self.post, response.context['page_obj'])
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'})
        )

        self.assertIn(self.post, response.context['page_obj'])
        self.assertEqual(response.context['group'], self.post.group)
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': 'darth'})
        )
        self.assertIn(self.post, response.context['page_obj'])
        self.assertEqual(response.context['author'], self.post.author)
        Group.objects.create(
            title='Test Group 2',
            slug='test_slug2',
        )
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test_slug2'})
        )
        self.assertNotIn(self.post, response.context['page_obj'])