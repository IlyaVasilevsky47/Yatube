from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from ..models import Post, Comment

User = get_user_model()


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстоый пост'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        """Создание нового комментария."""
        comment = Comment.objects.count()
        from_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=from_data,
            follow=True
        )

        self.assertAlmostEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment + 1)
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                author=self.user,
                text='Тестовый комментарий',
            )
        )

    def test_add_comment_unauthorized_user(self):
        """Проверка анонимного пользователя для создания комментария."""
        from_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=from_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
