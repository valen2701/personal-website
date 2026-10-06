from django.test import TestCase
from django.urls import reverse

from .models import Comment, Post


class BlogTests(TestCase):
    def create_post(self, title, slug, published_at):
        return Post.objects.create(
            title=title,
            slug=slug,
            excerpt=f'Introducción a {title}',
            content=f'Contenido de {title}',
            media='blog/imagen.jpg',
            published_at=published_at,
        )

    def test_portfolio_navigation_links_to_the_blog(self):
        response = self.client.get(reverse('portfolio:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/blog/">Blog</a>')
        self.assertContains(response, 'href="/static/styles.css"')

    def test_blog_page_uses_root_static_url_and_renders(self):
        response = self.client.get(reverse('blog:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/static/blog/blog.css"')

    def test_index_shows_posts_in_reverse_chronological_order(self):
        older = self.create_post('Entrada vieja', 'entrada-vieja', '2026-09-01T12:00:00Z')
        newer = self.create_post('Entrada nueva', 'entrada-nueva', '2026-10-01T12:00:00Z')

        response = self.client.get(reverse('blog:index'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['posts']), [newer, older])

    def test_detail_accepts_a_comment_for_that_post(self):
        post = self.create_post('Mi entrada', 'mi-entrada', '2026-10-01T12:00:00Z')

        detail_response = self.client.get(post.get_absolute_url())
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'href="/media/blog/imagen.jpg"')

        response = self.client.post(
            reverse('blog:detail', kwargs={'slug': post.slug}),
            {'author_name': 'Valeria', 'body': '¡Me gustó mucho!'},
        )

        self.assertRedirects(response, f'{post.get_absolute_url()}#comentarios')
        self.assertEqual(Comment.objects.get().post, post)
        self.assertEqual(Comment.objects.get().author_name, 'Valeria')

    def test_detail_displays_validation_errors_without_creating_comment(self):
        post = self.create_post('Mi entrada', 'mi-entrada', '2026-10-01T12:00:00Z')

        response = self.client.post(
            reverse('blog:detail', kwargs={'slug': post.slug}),
            {'author_name': '', 'body': ''},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(Comment.objects.count(), 0)
