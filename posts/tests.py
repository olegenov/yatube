from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from .forms import PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


class TestPosts(TestCase):
    def setUp(self):
        self.client_not_auth = Client()
        self.client_auth = Client()
        self.user = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345'
        )
        self.user2 = User.objects.create_user(
            username='test', email='test.s@skynet.com', password='testest'
        )
        self.group1 = Group.objects.create(
            title='Test group',
            slug='111',
            description='Test group'
        )
        self.group2 = Group.objects.create(
            title='Test group 2',
            slug='222',
            description='Test group 2'
        )
        self.client_auth.force_login(self.user)
        cache.clear()

    def post_existing_check(self, post, response):
        if 'paginator' in response.context:
            self.assertIn(post, response.context['page'])
            self.assertEqual(post.text, response.context['page'][0].text)
            self.assertEqual(post.group, response.context['page'][0].group)
        elif 'post' in response.context:
            self.assertEqual(post, response.context['post'])
            self.assertEqual(post.text, response.context['post'].text)
            self.assertEqual(post.group, response.context['post'].group)
        else:
            self.fail()

    def test_profile(self):
        response = self.client_not_auth.get(
            reverse(
                'profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['profile'], User)
        self.assertEqual(
            response.context['profile'].username,
            self.user.username
        )

    def test_new_post_not_auth(self):
        response = self.client_not_auth.post(
            reverse('new_post'),
            {'text': 'Test post 1'},
            follow=True
        )
        self.assertRedirects(
            response,
            '%s?next=/new/' % reverse('login'),
            status_code=302
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_new_post_auth(self):
        response = self.client_auth.post(
            reverse('new_post'),
            {'text': 'Test post 2'},
        )
        self.assertRedirects(
            response,
            reverse(
                'profile',
                kwargs={
                    'username': self.user.username
                }
            ),
            status_code=302
        )
        self.assertEqual(Post.objects.count(), 1)

    def test_post(self):
        self.post = Post.objects.create(
            text='Test post 3', author=self.user, group=self.group1
        )
        # Профиль.
        response = self.client_auth.get(
            reverse(
                'profile',
                kwargs={'username': self.user.username}
            )
        )
        self.post_existing_check(self.post, response)
        # Главная страница.
        response = self.client_auth.get(reverse('index'))
        self.post_existing_check(self.post, response)
        # Страница поста.
        response = self.client_auth.get(
            reverse(
                'post',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.pk
                }
            )
        )
        self.post_existing_check(self.post, response)
        # Группа.
        response = self.client_auth.get(
            reverse(
                'group',
                kwargs={
                    'slug': self.group1.slug,
                }
            )
        )
        self.post_existing_check(self.post, response)

    def test_post_edit(self):
        # Изменение группы и текста.
        self.post = Post.objects.create(
            text='Test post 4', author=self.user, group=self.group1
        )
        response = self.client_auth.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id,
                }
            ),
            {'text': 'Test post 4 edited', 'group': self.group2.id},
        )
        self.post_edited = Post.objects.get(pk=self.post.id)
        # Проверка редиректа.
        self.assertRedirects(
            response,
            reverse(
                'post',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.pk
                }
            ),
            status_code=302
        )
        # Профиль.
        response = self.client_auth.get(
            reverse(
                'profile',
                kwargs={'username': self.user.username}
            )
        )
        self.post_existing_check(self.post_edited, response)
        # Главная страница.
        response = self.client_auth.get(reverse('index'))
        self.post_existing_check(self.post_edited, response)
        # Страница поста.
        response = self.client_auth.get(
            reverse(
                'post',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.pk
                }
            )
        )
        self.post_existing_check(self.post_edited, response)
        # Группа.
        response = self.client_auth.get(
            reverse(
                'group',
                kwargs={
                    'slug': self.group1.slug,
                }
            )
        )
        self.assertNotIn(self.post_edited, response.context['page'])
        response = self.client_auth.get(
            reverse(
                'group',
                kwargs={
                    'slug': self.group2.slug,
                }
            )
        )
        self.post_existing_check(self.post_edited, response)

    def test_post_delete_not_auth(self):
        self.post = Post.objects.create(
            text='Test post 4', author=self.user, group=self.group1
        )
        self.client_not_auth.get(
            reverse(
                'post_delete',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id,
                }
            ),
            HTTP_REFERER=reverse('index')
        )
        self.assertEqual(Post.objects.count(), 1)

    def test_post_delete_auth(self):
        # Удаление.
        self.post = Post.objects.create(
            text='Test post 4', author=self.user, group=self.group1
        )
        response = self.client_auth.get(
            reverse(
                'post_delete',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id,
                }
            ),
            HTTP_REFERER=reverse('index')
        )
        self.assertEqual(Post.objects.count(), 0)
        # Профиль.
        response = self.client_auth.get(
            reverse(
                'profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertNotIn(self.post, response.context['page'])
        # Главная страница.
        response = self.client_auth.get(reverse('index'))
        self.assertNotIn(self.post, response.context['page'])
        # Страница поста.
        response = self.client_auth.get(
            reverse(
                'post',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.pk
                }
            )
        )
        self.assertEqual(response.status_code, 404)
        # Группа.
        response = self.client_auth.get(
            reverse(
                'group',
                kwargs={
                    'slug': self.group1.slug,
                }
            )
        )
        self.assertNotIn(self.post, response.context['page'])

    def test_follow_post(self):
        self.follow = Follow.objects.create(user=self.user, author=self.user2)
        self.post = Post.objects.create(author=self.user2, text='Text post 6')
        response = self.client_auth.get(
            reverse(
                'follow_index',
            )
        )
        self.post_existing_check(self.post, response)
        
    def test_not_follow_post(self):
        self.post = Post.objects.create(author=self.user2, text='Text post 7')
        response = self.client_auth.get(
            reverse(
                'follow_index',
            )
        )
        self.assertNotIn(self.post, response.context['page'])


class TestError(TestCase):
    def test_404(self):
        response = self.client.get(
            '/notexisting/',
            follow=True
        )
        self.assertEqual(response.status_code, 404)


class TestImage(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345'
        )
        self.client.force_login(self.user)
        self.group = Group.objects.create(
            title='Test group',
            slug='111',
            description='Test group'
        )
        cache.clear()

    def test_not_img(self):
        text_txt = b'Test text'
        txt = SimpleUploadedFile('text.txt', text_txt)
        response = self.client.post(
            reverse(
                'new_post',
            ), 
            {
                'text': 'post with image 1',
                'image': txt,
                'group': self.group.id
            }
        )
        form = response.context['form']
        self.assertFormError(
            response,
            'form',
            'image',
            'Загрузите правильное изображение.' + 
            ' Файл, который вы загрузили, поврежден или' +
            ' не является изображением.'
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(Post.objects.count(), 0)

    def test_img(self):
        img_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        img = SimpleUploadedFile('img.jpg', img_jpg)
        response = self.client.post(
            reverse(
                'new_post',
            ), 
            {
                'text': 'post with image 1',
                'image': img,
                'group': self.group.id
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)
        # Страница поста.
        response = self.client.get(
            reverse(
                'post',
                kwargs={
                    'username': self.user.username,
                    'post_id': Post.objects.first().id
                }
            )
        )
        self.assertContains(response, '<img', status_code=200)
        # Профиль.
        response = self.client.get(
            reverse(
                'profile',
                kwargs={
                    'username': self.user.username,
                }
            )
        )
        self.assertContains(response, '<img', status_code=200)
        # Главная страница.
        response = self.client.get(
            reverse(
                'index',
            )
        )
        self.assertContains(response, '<img', status_code=200)
        # Группа.
        response = self.client.get(
            reverse(
                'group',
                kwargs={
                    'slug': self.group.slug
                }
            )
        )
        self.assertContains(response, '<img', status_code=200)


class TestCache(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345'
        )

    def test_cache_index(self):
        response = self.client.get(reverse('index'))
        posts = response.context['page']
        posts_count = len(posts)
        self.assertEqual(posts_count, 0)
        self.post = Post.objects.create(author=self.user, text='Text post 6')
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, self.post.text)
        cache.clear()
        response = self.client.get(reverse('index'))
        posts = response.context['page']
        posts_count = len(posts)
        self.assertEqual(posts_count, 1)


class TestFollow(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345'
        )
        self.user2 = User.objects.create_user(
            username='t1000', email='t1000.s@skynet.com', password='54321'
        )
        self.client.force_login(self.user1)
    
    def test_follow(self):
        response = self.client.get(
            reverse(
                'profile_follow',
                kwargs={
                    'username': self.user2.username
                }
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollow(self):
        Follow.objects.create(
            user=self.user1,
            author=self.user2
        )
        response = self.client.get(
            reverse(
                'profile_unfollow',
                kwargs={
                    'username': self.user2.username
                }
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Follow.objects.count(), 0)


class TestComments(TestCase):
    def setUp(self):
        self.client_auth = Client()
        self.client_not_auth = Client()
        self.user = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345'
        )
        self.client_auth.force_login(self.user)

    def test_comment_not_auth(self):
        self.post = Post.objects.create(author=self.user, text='Text post 7')
        response = self.client_not_auth.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ),
            {'text': 'Comment 1'},
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_auth(self):
        self.post = Post.objects.create(author=self.user, text='Text post 7')
        text = 'Test comment 1'
        response = self.client_auth.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ),
            {'text': text},
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.comment = Comment.objects.first()
        self.assertEqual(self.comment.text, text)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.post.id, self.post.id)
