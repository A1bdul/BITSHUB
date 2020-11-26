from django.contrib import admin

from Site.models import Article, Comment, NewsLetter

admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(NewsLetter)