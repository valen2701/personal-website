from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm
from .models import Post


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
