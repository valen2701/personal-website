from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm
from .models import Comment, CommentLike, Post, PostLike


def index(request):
    order = request.GET.get('order', 'newest')
    if order == 'oldest':
        posts = Post.objects.order_by('published_at', '-pk')
    elif order == 'most_liked':
        posts = Post.objects.annotate(likes_count=Count('likes')).order_by('-likes_count', '-published_at')
    else:
        posts = Post.objects.order_by('-published_at', '-pk')

    categories = [category for category, _ in Post.CATEGORY_CHOICES]
    category_groups = [
        {
            'name': category,
            'posts': [post for post in posts if post.category == category],
        }
        for category in categories
    ]
    post_likes = set()
    if request.user.is_authenticated:
        post_likes = set(PostLike.objects.filter(user=request.user).values_list('post_id', flat=True))

    return render(
        request,
        'blog/blog.html',
        {
            'posts': posts,
            'categories': categories,
            'category_groups': category_groups,
            'order': order,
            'user_post_likes': post_likes,
        },
    )


@login_required
@require_POST
def toggle_post_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()

    return JsonResponse({
        'liked': created,
        'likes_count': post.likes.count(),
    })


@login_required
@require_POST
def toggle_comment_like(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    like, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
    if not created:
        like.delete()

    return JsonResponse({
        'liked': created,
        'likes_count': comment.likes.count(),
    })


def detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    form = CommentForm(request.POST or None)
    user_post_likes = set()
    user_comment_likes = set()
    if request.user.is_authenticated:
        user_post_likes = set(PostLike.objects.filter(user=request.user).values_list('post_id', flat=True))
        user_comment_likes = set(CommentLike.objects.filter(user=request.user).values_list('comment_id', flat=True))

    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        return redirect(post.get_absolute_url() + '#comentarios')

    return render(
        request,
        'blog/blog.html',
        {
            'post': post,
            'form': form,
            'user_post_likes': user_post_likes,
            'user_comment_likes': user_comment_likes,
        },
    )


@require_POST
@permission_required('blog.delete_comment', raise_exception=True)
def delete_comment(request: HttpRequest, comment_id: int) -> HttpResponse:
    comment = get_object_or_404(Comment, pk=comment_id)
    post_url = comment.post.get_absolute_url()
    comment.delete()
    return redirect(f'{post_url}#comentarios')
