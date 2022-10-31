from django import forms

from .models import Comment, Post

AUTHORS_LIST = [
    'донцова',
    'спаркс',
    'джеймс',
    'майер',
    'коэльо'
]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        """Заменяет слова из списка звездочками."""
        comment = self.cleaned_data['text']
        comment_text = comment.split()
        for i in range(len(comment_text)):
            if comment_text[i].lower() in AUTHORS_LIST:
                comment_text[i] = len(comment_text[i]) * '*'
        return (' '.join(comment_text))
