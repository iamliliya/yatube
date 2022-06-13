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

# Теперь все комментарии будут писаться строчными буквами,
# не могу пока сообразить, как сделать так,
# чтобы это работало только на нужные слова

    # def clean_text(self):
    #     comment = self.cleaned_data['text']
    #     comment_text = comment.lower().split()
    #     common_words = set(comment_text) & set(AUTHORS_LIST)
    #     for i in range(len(comment_text)):
    #         if comment_text[i] in common_words:
    #             comment_text[i] = len(comment_text[i]) * '*'
    #     return (' '.join(comment_text))
