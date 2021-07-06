import os

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.urls import reverse
from django.http import request

from .forms import PostForm, CommentForm, ProfilePhotoForm
from .models import Group, Post, Comment, Follow, ProfilePhoto

User = get_user_model()


@cache_page(20,  key_prefix='index_page')
def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'paginator': paginator, 'page': page}
    )


@login_required
def new_post(request):
    post_exists = False

    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(
            request,
            'posts/new_post.html',
            {'form': form, 'exists': post_exists}
        )

    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect(
        reverse(
            'profile',
            kwargs={
                'username': post.author.username
            }
        )
    )


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    
    if ProfilePhoto.objects.filter(user=profile).exists():
        photo = ProfilePhoto.objects.get(user=profile).photo
    else:
        photo = os.path.abspath('media/profile.jpg')
    
    post_list = profile.posts.order_by('-pub_date')
    post_amount = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    follows_count = profile.follower.count()
    followers_count = profile.following.count()
    following = False

    if request.user.is_authenticated:
        if Follow.objects.filter(
            user=request.user, 
            author=profile
        ).exists(): 
            following = True

    return render(
        request,
        'posts/profile.html',
        {
            'profile': profile,
            'paginator': paginator,
            'page': page,
            'amount': post_amount,
            'following': following,
            'follows': follows_count,
            'followers': followers_count,
            'photo': photo
        }
    )


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)

    if ProfilePhoto.objects.filter(user=profile).exists():
        photo = ProfilePhoto.objects.get(user=profile).photo
    else:
        photo = os.path.abspath('media/profile.jpg')

    post = get_object_or_404(Post, pk=post_id, author=profile)
    post_amount = profile.posts.count()
    form = CommentForm()
    comments = post.comments.order_by('-created')
    follows_count = profile.follower.count()
    followers_count = profile.following.count()

    return render(
        request,
        'posts/post.html',
        {
            'profile': profile,
            'post': post,
            'amount': post_amount,
            'items': comments,
            'form': form,
            'follows': follows_count,
            'followers': followers_count,
            'photo': photo
        }
    )


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)

    if request.user != post.author:
        return redirect('post', username=profile, post_id=post.pk)

    post_exists = True

    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

    if not form.is_valid():
        return render(
            request,
            'posts/new_post.html',
            {'form': form, 'exists': post_exists, 'post': post}
        )

    form.save()

    return redirect('post', username=profile, post_id=post.pk)


@login_required
def post_delete(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)

    if request.user != post.author:
        return redirect('index')

    post.delete()
    url = request.META.get('HTTP_REFERER')
    return redirect(url)


def page_not_found(request, exception):
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    form = CommentForm(request.POST or None)

    if not form.is_valid():
        return render(
            request,
            'posts/post.html',
            {'form': form, 'post': post}
        )

    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()

    return redirect(
        reverse(
            'post',
            kwargs={
                'username': username,
                'post_id': post_id
            }
        )
    )


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    url = reverse(
        'profile',
        kwargs={
            'username': username,
        }
    )
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect(
            url
        )
    Follow.objects.get_or_create(
        user=request.user,
        author=author
    )
    return redirect(
        url
    )


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    url = reverse(
        'profile',
        kwargs={
            'username': username,
        }
    )
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()

    return redirect(
        url
    )


@login_required
def edit_photo(request, username):
    profile = get_object_or_404(User, username=username)

    if ProfilePhoto.objects.filter(user=profile).exists():
        photo = ProfilePhoto.objects.get(user=profile).photo
    else:
        photo = None 

    if request.user != profile:
        return redirect('profile', username=profile)

    form = ProfilePhotoForm(request.POST or None, files=request.FILES or None, instance=photo)

    if not form.is_valid():
        return render(
            request,
            'profile_photo.html',
            {'form': form, 'profile': profile}
        )

    try:
        photo = ProfilePhoto.objects.get(user=profile)
        photo.delete()
    except:
        photo = None

    photo = form.save(commit=False)
    photo.user = request.user
    photo.save()

    return redirect('profile', username=profile)
