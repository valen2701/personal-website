import mimetypes

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('deportes', 'Deportes'),
        ('musica', 'Música'),
        ('desarrollo web', 'Desarrollo web'),
        ('gaming', 'Gaming'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    excerpt = models.CharField(max_length=300)
    content = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    media = models.FileField(upload_to='img/', blank=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-published_at', '-pk']

    def __str__(self):
        return self.title

    @property
    def media_content_type(self):
        if not self.media:
            return ''
        return mimetypes.guess_type(self.media.name)[0] or ''

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=80, verbose_name='nombre')
    body = models.TextField(max_length=2000, verbose_name='comentario')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comentario de {self.author_name} en {self.post}'


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_post_like')
        ]

    def __str__(self):
        return f'{self.user} le dio like a {self.post}'


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['comment', 'user'], name='unique_comment_like')
        ]

    def __str__(self):
        return f'{self.user} le dio like a {self.comment}'
