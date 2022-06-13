import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from posts.models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
            group=cls.group,
            pub_date=timezone.now
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_with_group(self):
        """Валидная форма создает запись в Post с указанием группы."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test text with group',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'darth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Test text with group',
                group=self.group,
                author=self.user
            ).exists()
        )

    def test_create_post_without_group(self):
        """Валидная форма создает запись в Post без указания группы."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Test text for a post without group'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'darth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Test text for a post without group',
                author=self.user,
                group=None
            ).exists()
        )

    def test_edit_post_authorized_group_unchanged(self):
        """Валидная форма редактирует запись в Post, группа не меняется."""
        form_data = {
            'text': 'Test text 2',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text='Test text 2',
                group=self.group,
                author=self.user,
                pub_date=self.post.pub_date,
                id=self.post.id
            ).exists()
        )

    def test_edit_post_authorized_change_group(self):
        """Валидная форма редактирует запись в Post, группа меняется."""
        group2 = Group.objects.create(
            title='Test group for change',
            slug='test_group_change'
        )

        form_data = {
            'text': 'Test text with group change',
            'group': group2.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text='Test text with group change',
                group=group2,
                author=self.user,
                pub_date=self.post.pub_date,
                id=self.post.id
            ).exists()
        )

    def test_edit_post_unauthorized(self):
        """Неавторизованный пользователь не редактирует запись в Post."""
        post3 = Post.objects.create(
            text='Test text for unauthorized user',
            author=self.user,
            group=self.group,
        )

        form_data = {
            'text': 'Test text for unauthorized user changed',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post3.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{post3.id}/edit/'
        )
        self.assertTrue(
            Post.objects.filter(
                text='Test text for unauthorized user',
                group=self.group,
                author=self.user,
                pub_date=post3.pub_date,
                id=post3.id
            ).exists()
        )

    def test_edit_post_non_author(self):
        """Не автор поста не редактирует запись в Post."""
        post4 = Post.objects.create(
            text='Test text for non author',
            author=self.user,
            group=self.group
        )

        form_data = {
            'text': 'Test text for non author changed',
            'group': self.group.id
        }
        non_author = User.objects.create(username='obiwan')
        authorized_client2 = Client()
        authorized_client2.force_login(non_author)

        response = authorized_client2.post(
            reverse('posts:post_edit', kwargs={'post_id': post4.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': post4.id}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text='Test text for non author',
                group=self.group,
                author=self.user,
                pub_date=post4.pub_date,
                id=post4.id
            ).exists()
        )

    def test_create_post_with_image(self):
        """Валидная форма создает запись в Post с картинкой."""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Test text with image',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'darth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Test text with image',
                group=self.group,
                author=self.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_authorized_user_can_comment(self):
        """"Авторизованный пользователь может оставить комментарий"""
        count = Comment.objects.count()
        form_data = {'text': 'Test comment'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                text='Test comment',
                author=self.user
            ).exists()
        )

    def test_guest_user_cannot_comment(self):
        """Неавторизованный пользователь не может оставить комментарий"""
        count = Comment.objects.count()
        form_data = {'text': 'Test comment'}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), count)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )

    # def test_comment_validator(self):
    #     """Проверяем валидатор"""
    #     count = Comment.objects.count()
    #     form_data = {'text': 'Донцова и мистер Спаркс'}
    #     response = self.authorized_client.post(
    #         reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
    #         data=form_data,
    #         follow=True
    #     )
    #     self.assertEqual(Comment.objects.count(), count + 1)
    #     self.assertRedirects(response, reverse(
    #         'posts:post_detail', kwargs={'post_id': self.post.id})
    #     )
    #     self.assertTrue(
    #         Comment.objects.filter(
    #             post=self.post,
    #             text='******* и мистер ******',
    #             author=self.user
    #         ).exists()
    #     )
