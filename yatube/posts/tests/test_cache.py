from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, User


class PostCacheTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='darth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text'
        )

    def test_index_cache(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.post.delete()
        response2 = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response2.content)
        cache.clear()
        response3 = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response2.content, response3.content)
