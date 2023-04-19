from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.cache import cache
from django.urls import reverse
from .models import Post, Group, User, Follow, Comment
from time import time
import os

class BlogTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.post_content = 'Test post content'
        self.group = Group.objects.create(title='Test Group', slug='test-group', description='Test group description')

    def test_user_profile_creation(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/{self.user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_create_post(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/new', {'text': self.post_content, 'group': self.group.id})
        self.assertEqual(response.status_code, 302)  # post creation redirects

    def test_unauthenticated_user_cannot_create_post(self):
        response = self.client.post('/new', {'text': self.post_content})
        self.assertRedirects(response, '/auth/login/?next=%2Fnew')

    def test_user_can_edit_post(self):
        self.client.login(username='testuser', password='testpassword')
        self.client.post('/new', {'text': self.post_content, 'group': self.group.id})
        post = Post.objects.get(text=self.post_content)
        edited_post_content = 'Edited post content'

        self.client.post(f'/{self.user.username}/{post.id}/edit/', {'text': edited_post_content})
        post.refresh_from_db()
        self.assertEqual(post.text, edited_post_content)
        
# новыетесты

    def test_post_with_image_has_img_tag(self):
        self.client.login(username='testuser', password='testpassword')
        image_path = os.path.join(os.path.dirname(__file__), 'test_image.jpg')
        with open(image_path, 'rb') as img:
            uploaded_image = SimpleUploadedFile(img.name, img.read())
            self.client.post('/new', {'text': self.post_content, 'image': uploaded_image, 'group': self.group.id})
        
        post = Post.objects.get(text=self.post_content)
        response = self.client.get(f'/{self.user.username}/{post.id}/')
        self.assertContains(response, '<img')

    def test_image_displayed_on_pages(self):
        self.client.login(username='testuser', password='testpassword')
        image_path = os.path.join(os.path.dirname(__file__), 'test_image.jpg')
        with open(image_path, 'rb') as img:
            uploaded_image = SimpleUploadedFile(img.name, img.read())
            self.client.post('/new', {'text': self.post_content, 'image': uploaded_image, 'group': self.group.id})
        
        post = Post.objects.get(text=self.post_content)

        response_index = self.client.get('/')
        response_profile = self.client.get(f'/{self.user.username}/')
        response_group = self.client.get(f'/group/{self.group.slug}/')

        for response in [response_index, response_profile, response_group]:
            self.assertContains(response, '<img')

    def test_non_image_upload_protection(self):
        self.client.login(username='testuser', password='testpassword')
        non_image_path = os.path.join(os.path.dirname(__file__), 'test_file.txt')
        with open(non_image_path, 'rb') as non_img:
            uploaded_non_image = SimpleUploadedFile(non_img.name, non_img.read())
            response = self.client.post('/new', {'text': self.post_content, 'image': uploaded_non_image, 'group': self.group.id})
        self.assertEqual(response.status_code, 400)

class TestCache(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.group = Group.objects.create(title='test_group', slug='test_group', description='test_description')
        self.post = Post.objects.create(text='test_text', author=self.user, group=self.group)
        self.index_url = reverse('index')

    def test_cache_index_page(self):
        # Очистка кэша перед тестированием
        cache.clear()

        # Запрашиваем главную страницу и замеряем время выполнения запроса
        start_time = time()
        response1 = self.client.get(self.index_url)
        response1_time = time() - start_time

        # Получаем содержимое кэша
        cached_posts = cache.get('index_page')

        # Проверяем, что кэш содержит нужные данные
        self.assertIsNotNone(cached_posts)
        self.assertIn(self.post, cached_posts)

        # Запрашиваем главную страницу снова и замеряем время выполнения запроса
        start_time = time()
        response2 = self.client.get(self.index_url)
        response2_time = time() - start_time

        # Проверяем, что время выполнения запроса с кэшем меньше, чем без кэша
        self.assertLess(response2_time, response1_time)

        # Проверяем, что ответы содержат одинаковые данные
        self.assertContains(response1, self.post.text)
        self.assertContains(response2, self.post.text)

class FollowTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.post = Post.objects.create(text='Test post', author=self.user2)

    def test_follow_unfollow(self):
        self.client.login(username='user1', password='password123')

        response = self.client.post(reverse('profile_follow', kwargs={'username': self.user2.username}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Follow.objects.filter(user=self.user1, author=self.user2).exists())

        response = self.client.post(reverse('profile_unfollow', kwargs={'username': self.user2.username}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Follow.objects.filter(user=self.user1, author=self.user2).exists())

    def test_new_post_in_feed(self):
        Follow.objects.create(user=self.user1, author=self.user2)
        self.client.login(username='user1', password='password123')

        response = self.client.get(reverse('follow_index'))
        self.assertContains(response, 'Test post')

        self.client.logout()
        self.client.login(username='user2', password='password123')

        response = self.client.get(reverse('follow_index'))
        self.assertNotContains(response, 'Test post')

    def test_comment_auth(self):
        self.client.login(username='user1', password='password123')

        response = self.client.post(reverse('add_comment', kwargs={'username': self.user2.username, 'post_id': self.post.id}), {'text': 'Test comment'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(text='Test comment', author=self.user1, post=self.post).exists())

        self.client.logout()

        response = self.client.post(reverse('add_comment', kwargs={'username': self.user2.username, 'post_id': self.post.id}), {'text': 'Test comment'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(text='Test comment', author=None, post=self.post).exists())
