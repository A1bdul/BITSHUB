from django.contrib import admin
from Site.models import Article, Comment, NewsLetter

admin.site.register(Comment)
admin.site.register(NewsLetter)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'Author')
    search_fields = ('title',)
    list_filter = ('title','Author')
    list_display_links = ('title',)


admin.site.register(Article, ArticleAdmin)