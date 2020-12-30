from django import forms
from tinymce.widgets import TinyMCE

from Site.models import Comment, Article


class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)


class UpdatePost(forms.ModelForm):
    class Meta:
        model = Article
        fields = {
            'title','body', 'cover_photo', 'status', 'snippet'
        }


class ArticleCreate(forms.ModelForm):
    body = forms.CharField(widget=TinyMCEWidget(attrs={'required': False, 'cols': 30, 'rows': 10}))

    class Meta:
        model = Article
        fields = {
            'title', 'cover_photo', 'snippet', 'status'
        }
