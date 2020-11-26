from django import forms
from Site.models import Comment, Article


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class UpdatePost(forms.ModelForm):
    category = forms.CharField(disabled=True, widget=forms.TextInput())

    class Meta:
        model = Article
        fields = {
            'title', 'body', 'cover_photo', 'status', 'snippet'
        }


class ArticleCreate(forms.ModelForm):
    snippet = forms.CharField(required=False)
    cover_photo = forms.ImageField(required=False)

    class Meta:
        model = Article
        fields = {
            'title', 'body', 'cover_photo', 'snippet', 'status'
        }
