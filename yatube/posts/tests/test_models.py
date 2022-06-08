from django.test import TestCase

from ..models import Group, Post, User, POST_TEXT_TRANCATE


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='This is a test text post'
        )

    def test_post_model_has_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = self.post
        expected_object_name = post.text[:POST_TEXT_TRANCATE]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        """Поля verbose_name соответствуют ожидаемому"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """Поля help_text соответствуют ожидаемому"""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Test description'
        )

    def test_group_model_has_correct_name(self):
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
