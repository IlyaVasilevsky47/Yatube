from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()
NO_POST_ID_TWO = 2


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        cache.clear()
        self.client = User.objects.create_user(username='client')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.client)
        self.authorized_auth = Client()
        self.authorized_auth.force_login(self.user)

    def test_url_exists_at_desired_location(self):
        """Проверка доступность страницы."""

        def test_url_status(url_client):
            for addres, user_status in url_client.items():
                with self.subTest(addres=addres):
                    response = user_status['user'].get(addres)
                    self.assertEqual(
                        response.status_code,
                        user_status['status'],
                        f'Адрес: {addres}'
                    )

        url_client_guest_client = {
            reverse('posts:index'): {
                'user': self.guest_client,
                'status': HTTPStatus.OK,
            },
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): {
                'user': self.guest_client,
                'status': HTTPStatus.OK,
            },
            reverse('posts:profile', kwargs={'username': 'auth'}): {
                'user': self.guest_client,
                'status': HTTPStatus.OK,
            },
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}): {
                'user': self.guest_client,
                'status': HTTPStatus.OK,
            },
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): {
                'user': self.guest_client,
                'status': HTTPStatus.FOUND,
            },
            reverse('posts:post_create'): {
                'user': self.guest_client,
                'status': HTTPStatus.FOUND,
            },
            reverse('posts:post_detail', kwargs={'post_id': NO_POST_ID_TWO}): {
                'user': self.guest_client,
                'status': HTTPStatus.NOT_FOUND,
            },
        }
        url_client_authorized_client = {
            reverse('posts:post_create'): {
                'user': self.authorized_client,
                'status': HTTPStatus.OK,
            },
        }
        url_client_authorized_auth = {
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): {
                'user': self.authorized_auth,
                'status': HTTPStatus.OK,
            },
        }

        test_url_status(url_client_guest_client)
        test_url_status(url_client_authorized_client)
        test_url_status(url_client_authorized_auth)

    def test_create_list_url_redirect_anonymous_on_admin_login(self):
        """Перенаправление анонимного пользователя на страницу логина."""
        redirection = {
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): '/auth/login/?next=/posts/1/edit/',
            reverse('posts:post_create'): '/auth/login/?next=/create/',
        }
        for address, tempalte in redirection.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, tempalte)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_tempaltes = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'auth'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': NO_POST_ID_TWO}
            ): 'core/404.html',
        }
        for address, tempalte in url_tempaltes.items():
            with self.subTest(address=address):
                response = self.authorized_auth.get(address)
                self.assertTemplateUsed(response, tempalte)
