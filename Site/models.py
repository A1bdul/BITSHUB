from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from froala_editor.fields import FroalaField


class NewsLetter(models.Model):
    newsletter = models.EmailField()

    def __str__(self):
        return str(self.newsletter)


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status="published")


class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    # Classifying our model manager on whether the author is ready to publish it or not....
    objects = models.Manager()
    published = PublishedManager()
    #

    #  basis features that will be in our article
    title = models.CharField(max_length=250)
    Author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE)
    body = FroalaField(theme='dark')
    cover_photo = models.CharField(max_length=300, blank=True)
    slug = models.SlugField(max_length=100)
    snippet = models.CharField(max_length=150, blank=True, null=True)
    publish_date = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    #

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-id']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[self.id, self.slug])

    def total_likes(self):
        return self.likes.count


# @receiver(pre_save, sender=Article)
# def pre_save_slug(**kwargs):
#     slug = slugify(kwargs['instance'].title)
#     kwargs['instance'].slug = slug


class Comment(models.Model):
    post = models.ForeignKey(Article, on_delete=models.CASCADE)
    reply = models.ForeignKey('Comment', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} {}'.format(self.post.title, str(self.user.username))
