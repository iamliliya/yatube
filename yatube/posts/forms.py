from django import forms

from .models import Comment, Post

AUTHORS_LIST = [
    'донцова',
    'спаркс',
    'джеймс',
    'майер',
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
        text = self.cleaned_data['text']
        text_lower = str.casefold(text)
        change_word = ''
        if text_lower in AUTHORS_LIST:
            for i in text_lower:
                change_word = change_word + '*'
            return change_word
        else:
            return text
