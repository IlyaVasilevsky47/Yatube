from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client

from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


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
            id=1,
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
            '/': {'user': self.guest_client, 'status': HTTPStatus.OK},
            '/group/test-slug/': {
                'user': self.guest_client, 'status': HTTPStatus.OK
            },
            '/profile/auth/': {
                'user': self.guest_client, 'status': HTTPStatus.OK
            },
            '/posts/1/': {
                'user': self.guest_client, 'status': HTTPStatus.OK
            },
            '/posts/1/edit/': {
                'user': self.guest_client, 'status': HTTPStatus.FOUND
            },
            '/create/': {
                'user': self.guest_client, 'status': HTTPStatus.FOUND
            },
            '/unexisting_page/': {
                'user': self.guest_client, 'status': HTTPStatus.NOT_FOUND
            },
        }
        url_client_authorized_client = {
            '/create/': {
                'user': self.authorized_client, 'status': HTTPStatus.OK
            },
        }
        url_client_authorized_auth = {
            '/posts/1/edit/': {
                'user': self.authorized_auth, 'status': HTTPStatus.OK
            },
        }

        test_url_status(url_client_guest_client)
        test_url_status(url_client_authorized_client)
        test_url_status(url_client_authorized_auth)

    def test_create_list_url_redirect_anonymous_on_admin_login(self):
        """Перенаправление анонимного пользователя на страницу логина."""
        redirection = {
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for address, tempalte in redirection.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, tempalte)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_tempaltes = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }
        for address, tempalte in url_tempaltes.items():
            with self.subTest(address=address):
                response = self.authorized_auth.get(address)
                self.assertTemplateUsed(response, tempalte)
