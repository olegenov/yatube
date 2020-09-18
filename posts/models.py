from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=30)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(help_text='Что нового?', verbose_name='Текст')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True, null=True, related_name='posts',
        verbose_name='Сообщество',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True, null=True,
        verbose_name='Изображение'
    )

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        help_text='Добавьте комментарий', 
        verbose_name='Текст'
    )
    created = models.DateTimeField('date published', auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    class Meta:
        unique_together = ['user', 'author']


class ProfilePhoto(models.Model):
    photo = models.ImageField(
        upload_to='users/',
        blank=True, null=True,
        verbose_name='Аватар'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='profile_photo'
    )
