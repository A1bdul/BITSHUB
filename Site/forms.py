from django import forms
from Site.models import Comment, Article


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)


class UpdatePost(forms.ModelForm):

    class Meta:
        model = Article
        fields = {
            'title', 'body', 'cover_photo', 'status', 'snippet'
        }


class ArticleCreate(forms.ModelForm):

    class Meta:
        model = Article
        fields = {
            'title', 'body', 'cover_photo', 'snippet', 'status'
        }
