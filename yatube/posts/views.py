from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow

TIME_CASH = 5
LIMIT = 10
ONE_FOLLOW = 1


@cache_page(TIME_CASH, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    paginator = Paginator(post_list, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user)
    paginator = Paginator(post_list, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'username': user,
        'page_obj': page_obj,
    }
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=user
        ).exists()
        context['following'] = following
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    posts = get_object_or_404(Post, pk=post_id)
    user_post = Post.objects.filter(author=posts.author)
    form = CommentForm()
    comments = Comment.objects.filter(post=post_id)
    context = {
        'posts': posts,
        'form': form,
        'comments': comments,
        'user_post': user_post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    username = request.user.username
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    user = request.user
    posts = get_object_or_404(Post, id=post_id, author=user)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=posts
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'is_edit': is_edit,
        'posts': posts,
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    authors = Follow.objects.values('author').filter(user=request.user)
    post_queryset = Post.objects.filter(author__in=authors)
    paginator = Paginator(post_queryset, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    count = Follow.objects.filter(user=request.user, author=author).count()
    if request.user.username == username or count == ONE_FOLLOW:
        return redirect('posts:profile', username=username)
    Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
