import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from http import HTTPStatus

from ..models import Group, Post, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEST_POSTS_QUANTITY = 12
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост нулевой',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().setUpClass()
        # Удаляем директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.new_user = User.objects.create_user(username='new_user')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_new_user = Client()
        self.authorized_new_user.force_login(self.new_user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
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
        }
        # Проверка шаблонов
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_obj_correct_context(self):
        """Проверка 'page_obj' сформирован с правильным контекстом."""
        post_views = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        ]
        for reverse_name in post_views:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.author, self.user)
                self.assertEqual(first_object.text, 'Тестовый пост нулевой')
                self.assertEqual(first_object.group, self.group)
                self.assertEqual(first_object.image, 'posts/small.gif')

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        ))
        self.assertEqual(response.context['group'].title, 'Тестовая группа')
        self.assertEqual(response.context['group'].slug, 'test-slug')
        self.assertEqual(
            response.context['group'].description, 'Тестовое описание'
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом username."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}
        ))
        self.assertEqual(response.context['username'].username, 'auth')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом posts."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(response.context['posts'].author, self.user)
        self.assertEqual(response.context['user_post'].count(), self.post.id)
        self.assertEqual(
            response.context['posts'].text, 'Тестовый пост нулевой'
        )
        self.assertEqual(response.context['posts'].group, self.group)
        self.assertEqual(response.context['posts'].image, 'posts/small.gif')

    def test_form_page_show_correct_context(self):
        """Проверка PostForm страниц."""
        reverse_form = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for reverse_name in reverse_form:
            response = self.authorized_client.get(reverse_name)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        """Проверка cache на странице index."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_update = Post.objects.get(id=1)
        post_update.text = 'Тестовый пост обновленный'
        first_object = response.context['page_obj'][0]
        self.assertNotEqual(first_object.text, post_update.text)

    def test_list_page_list(self):
        """Проверка paginator."""
        posts = []
        for nubers in range(TEST_POSTS_QUANTITY):
            posts.append(Post(
                author=self.user,
                text=f'Тестовый пост {nubers}',
                group=self.group
            ))
        Post.objects.bulk_create(posts)
        examination_pages = {
            reverse('posts:index'): 10,
            reverse('posts:index') + '?page=2': 3,
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): 10,
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ) + '?page=2': 3,
            reverse('posts:profile', kwargs={'username': 'auth'}): 10,
            reverse(
                'posts:profile', kwargs={'username': 'auth'}
            ) + '?page=2': 3,
        }
        # Проверка paginator
        for reverse_name, page in examination_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), page)

    def test_post_create_page_show_correct_context(self):
        """Проверка созадния поста."""
        group_new = Group.objects.create(
            title='Новая тестовая группа',
            slug='new-test-slug',
            description='Новое тестовое описание',
        )
        post_new = {
            'text': 'Новый тестовый пост',
            'group': group_new.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_new,
            follow=True
        )

        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'new-test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]

        for reverse_name in pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.author, self.user)
                self.assertEqual(first_object.text, 'Новый тестовый пост')
                self.assertEqual(first_object.group, group_new)

        self.assertFalse(
            Post.objects.filter(
                author=self.user,
                text='Новый тестовый пост',
                group=self.group.id
            ).exists()
        )

    def test_form_page_show_correct_context(self):
        """Проверка CommentForm страниц."""
        form_fields = {
            'text': forms.fields.CharField,
        }
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_comment_show_correct_context(self):
        """Проверка созадния комментария."""
        from_data = {
            'text': 'Тестовый комментарий'
        }
        new_post = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=from_data,
            follow=True
        )
        self.assertEqual(new_post.status_code, HTTPStatus.OK)
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context['comments'][0]
        self.assertEqual(first_object.post, self.post)
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, 'Тестовый комментарий')

    def test_follow_user_subscription(self):
        """Проверка подписки на автора."""
        response = self.authorized_new_user.post(
            reverse('posts:profile_follow', kwargs={'username': 'auth'}),
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Follow.objects.filter(
                user=self.new_user,
                author=self.user
            ).exists()
        )

    def test_follow_page_index_unsubscribe(self):
        """Проверка записей на подписанного пользователя."""
        Post.objects.create(
            author=self.user,
            text='Тестовый пост подписка',
            group=self.group,
        )
        unsubscribe = self.authorized_new_user.post(
            reverse('posts:profile_follow', kwargs={'username': 'auth'}),
            follow=True
        )
        self.assertEqual(unsubscribe.status_code, HTTPStatus.OK)

        response = self.authorized_new_user.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, 'Тестовый пост подписка')
        self.assertEqual(first_object.group, self.group)

    def test_follow_page_index_unsubscribe(self):
        """Проверка записей кто не подписан на пользователя."""
        Post.objects.create(
            author=self.new_user,
            text='Тестовый пост нового uwer',
            group=self.group,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertFalse(response.context['page_obj'])

    def test_follow_user_unsubscribe(self):
        """Проверка отдписки на автора."""
        response = self.authorized_new_user.post(
            reverse('posts:profile_unfollow', kwargs={'username': 'auth'}),
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(
            Follow.objects.filter(
                user=self.new_user,
                author=self.user
            ).exists()
        )
