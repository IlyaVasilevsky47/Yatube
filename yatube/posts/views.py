from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

TIME_CASH = 5
LIMIT = 6
ONE_FOLLOW = 1


@cache_page(TIME_CASH, key_prefix='index_page')
def index(request):
    return render(
        request,
        'posts/index.html',
        context={
            'page_obj': Paginator(Post.objects.all(), LIMIT).get_page(
                request.GET.get('page')
            ),
        },
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(
        request,
        'posts/group_list.html',
        context={
            'group': group,
            'page_obj': Paginator(
                Post.objects.filter(group=group), LIMIT
            ).get_page(
                request.GET.get('page')
            ),
        },
    )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'username': user,
        'page_obj': Paginator(
            Post.objects.filter(author=user), LIMIT
        ).get_page(
            request.GET.get('page')
        ),
    }
    if request.user.is_authenticated:
        context['following'] = Follow.objects.filter(
            user=request.user, author=user
        ).exists()
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    posts = get_object_or_404(Post, pk=post_id)
    return render(
        request,
        'posts/post_detail.html',
        context={
            'posts': posts,
            'form': CommentForm(),
            'comments': Comment.objects.filter(post=post_id),
            'user_post': Post.objects.filter(author=posts.author),
        },
    )


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    posts = get_object_or_404(Post, id=post_id, author=request.user)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=posts
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        'posts/create_post.html',
        context={
            'is_edit': True,
            'posts': posts,
            'form': form,
        },
    )


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
    return render(
        request,
        'posts/follow.html',
        context={
            'page_obj': Paginator(
                Post.objects.filter(
                    author__in=Follow.objects.values(
                        'author'
                    ).filter(user=request.user)
                ),
                LIMIT,
            ).get_page(request.GET.get('page'))
        },
    )


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
    Follow.objects.filter(
        user=request.user, author=User.objects.get(username=username)
    ).delete()
    return redirect('posts:profile', username=username)
