from django.contrib.auth.decorators import permission_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm
from .models import Comment, Post


def index(request):
    posts = Post.objects.all()
    return render(request, 'blog/blog.html', {'posts': posts})


def detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    form = CommentForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        return redirect(post.get_absolute_url() + '#comentarios')

    return render(request, 'blog/blog.html', {'post': post, 'form': form})


@require_POST
@permission_required('blog.delete_comment', raise_exception=True)
def delete_comment(request: HttpRequest, comment_id: int) -> HttpResponse:
    comment = get_object_or_404(Comment, pk=comment_id)
    post_url = comment.post.get_absolute_url()
    comment.delete()
    return redirect(f'{post_url}#comentarios')
