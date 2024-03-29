from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm, CommentForm
from .models import Follow, Group, Post, User


def paginator_for_all(post_list, request):
    """Паджинатор разбивает на страницы."""
    paginator = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Возвращает главную страницу."""
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = paginator_for_all(post_list, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Возвращает все посты из выбранной группы."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_posts.select_related('group').all()
    page_obj = paginator_for_all(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Возвращает посты выбранного пользователя."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author').all()
    page_obj = paginator_for_all(post_list, request)
    user = request.user
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=user, author=author).exists())
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Возвращает детальную информацию о посте."""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('post').all()
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Возвращает форму для создания поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    context = {
        'form': form,
    }
    return render(request, 'posts/create.html', context)


@login_required
def post_edit(request, post_id):
    """Возвращает форму для редактирования поста."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, 'posts/create.html', context)


@login_required
def add_comment(request, post_id):
    """Возвращает форму для создания комментария."""
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Возвращает посты пользователей, на которыз подписан юзер."""
    post_list = Post.objects.filter(
        author__following__user=request.user).select_related(
            'author', 'group').all()
    page_obj = paginator_for_all(post_list, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписывает пользователя на выбранного автора."""
    user = request.user
    author = User.objects.get(username=username)
    if user != author:
        Follow.objects.filter(
            user=user, author=author).get_or_create(user=user, author=author)
    return redirect('posts:profile', author.username)


@login_required
def profile_unfollow(request, username):
    """Отписывает пользователя от выбранного автора."""
    user = request.user
    author = User.objects.get(username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', author.username)
