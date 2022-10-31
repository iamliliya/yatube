from django.contrib import admin

from .models import Group, Post, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    """Класс для админки Post."""

    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
        'image',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Класс для админки Group."""

    list_display = (
        'pk',
        'title',
        'description',
        'slug',
    )
    search_fields = ('title', 'descripition',)


class CommentAdmin(admin.ModelAdmin):
    """Класс для админки Comment."""

    list_display = (
        'post',
        'pk',
        'text',
        'author',
    )
    search_fields = ('text',)


class FollowAdmin(admin.ModelAdmin):
    """Класс для админки Follow."""

    list_display = (
        'user',
        'author'
    )


admin.site.register(Comment, CommentAdmin)

admin.site.register(Post, PostAdmin)

admin.site.register(Group, GroupAdmin)

admin.site.register(Follow, FollowAdmin)
