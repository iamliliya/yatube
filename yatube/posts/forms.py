from django import forms

from .models import Post, Comment


AUTHORS_LIST = [
    'донцова',
    'николас спаркс',
    'э.л.джеймс',
    'стефани майер',
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
        text = str.casefold(text)
        change_word = ''
        if text in AUTHORS_LIST:
            for i in text:
                change_word = change_word + '*'
        return change_word
