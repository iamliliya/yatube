from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

TEST_POSTS_AMOUNT = 14
TEST_POST_ON_ONE_PAGE = 10


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='darth')

        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
        )

        objs = [
            Post(
                text=f'Test text {i}',
                author=cls.user,
                group=cls.group
            )
            for i in range(TEST_POSTS_AMOUNT)
        ]
        Post.objects.bulk_create(objs)

    def test_index_first_page_contains_ten_records(self):
        """Паджинатор показывает правильное количество
        постов на 1 странице index"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            TEST_POST_ON_ONE_PAGE
        )

    def test_index_second_page_contains_four_records(self):
        """Паджинатор показывает правильное количество
        постов на 2 странице index"""
        response = self.client.get('//?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            TEST_POSTS_AMOUNT - TEST_POST_ON_ONE_PAGE
        )

    def test_group_first_page_contains_ten_records(self):
        """Паджинатор показывает правильное количество
        постов на 1 странице group_list"""
        response = self.guest_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(
            len(response.context['page_obj']),
            TEST_POST_ON_ONE_PAGE
        )

    def test_group_second_page_contains_four_records(self):
        """Паджинатор показывает правильное количество
        постов на 2 странице group_list"""
        response = self.client.get(f'/group/{self.group.slug}/?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            TEST_POSTS_AMOUNT - TEST_POST_ON_ONE_PAGE
        )

    def test_profile_first_page_contains_ten_records(self):
        """Паджинатор показывает правильное количество
        постов на 1 странице profile"""
        response = self.guest_client.get(f'/profile/{self.user}/')
        self.assertEqual(
            len(response.context['page_obj']),
            TEST_POST_ON_ONE_PAGE
        )

    def test_profile_second_page_contains_four_records(self):
        """Паджинатор показывает правильное количество
        постов на 2 странице profile"""
        response = self.client.get(f'/profile/{self.user}/?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            TEST_POSTS_AMOUNT - TEST_POST_ON_ONE_PAGE
        )
