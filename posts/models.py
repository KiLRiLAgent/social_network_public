from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()

class Group(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_posts')
    group = models.ForeignKey(
    Group, on_delete=models.CASCADE, related_name='group_posts', blank=True, null=True
    )
    # поле для картинки
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    
    def __str__(self):
       # выводим текст поста 
       return self.text

    class Meta:
        ordering = ['-pub_date']
        
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self):
        return f'{self.author} - {self.text[:50]}'

    class Meta:
        ordering = ['-created']

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"