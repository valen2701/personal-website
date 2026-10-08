from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Comment, CommentLike, Post, PostLike


class BlogTests(TestCase):
    def create_post(self, title, slug, published_at, category='desarrollo web'):
        return Post.objects.create(
            title=title,
            slug=slug,
            excerpt=f'Introducción a {title}',
            content=f'Contenido de {title}',
            media='img/imagen.jpg',
            published_at=published_at,
            category=category,
        )

    def test_portfolio_navigation_links_to_the_blog(self):
        response = self.client.get(reverse('portfolio:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/blog/">Blog</a>')
        self.assertContains(response, 'href="/static/styles.css"')
        self.assertContains(response, 'href="/accounts/login/?next=/">')

    def test_blog_navigation_links_to_the_portfolio_and_login(self):
        response = self.client.get(reverse('blog:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/accounts/login/?next=/blog/">')

    def test_authenticated_navigation_offers_post_logout_on_both_pages(self):
        user = get_user_model().objects.create_user(
            username='lector',
            password='test-password',
        )
        self.client.force_login(user)

        for url, next_url in (
            (reverse('portfolio:index'), '/'),
            (reverse('blog:index'), '/blog/'),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertContains(response, 'action="/accounts/logout/"')
                self.assertContains(response, f'value="{next_url}"')
                self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_login_authenticates_user_and_returns_to_requested_page(self):
        user = get_user_model().objects.create_user(
            username='lector',
            password='test-password',
        )

        response = self.client.post(
            reverse('login'),
            {'username': 'lector', 'password': 'test-password', 'next': '/blog/'},
        )

        self.assertRedirects(response, '/blog/')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_login_creates_a_new_user_when_it_does_not_exist(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'nuevo-lector', 'password': 'test-password', 'next': '/blog/'},
        )

        self.assertRedirects(response, '/blog/')
        self.assertTrue(get_user_model().objects.filter(username='nuevo-lector').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), get_user_model().objects.get(username='nuevo-lector').pk)

    def test_logout_ends_session_and_returns_to_requested_page(self):
        user = get_user_model().objects.create_user(
            username='lector',
            password='test-password',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('logout'), {'next': '/blog/'})

        self.assertRedirects(response, '/blog/')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_rejects_external_redirect(self):
        user = get_user_model().objects.create_user(
            username='lector',
            password='test-password',
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse('logout'),
            {'next': 'https://example.com/'},
        )

        self.assertRedirects(response, reverse('portfolio:index'))

    def test_blog_page_uses_root_static_url_and_renders(self):
        response = self.client.get(reverse('blog:index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog.html')
        self.assertContains(response, 'href="/static/styles.css"')
        self.assertContains(response, 'href="/static/blog/blog.css"')

    def test_post_media_is_stored_inside_blog_static_folder(self):
        self.assertEqual(settings.MEDIA_ROOT, Path(settings.BASE_DIR) / 'blog' / 'static')
        self.assertEqual(settings.MEDIA_URL, '/media/')
        self.assertEqual(Post._meta.get_field('media').upload_to, 'img/')

    def test_index_shows_posts_in_reverse_chronological_order(self):
        older = self.create_post('Entrada vieja', 'entrada-vieja', '2026-09-01T12:00:00Z')
        newer = self.create_post('Entrada nueva', 'entrada-nueva', '2026-10-01T12:00:00Z')

        response = self.client.get(reverse('blog:index'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['posts']), [newer, older])
        self.assertContains(response, '<img class="post-image"')

    def test_index_groups_posts_by_category(self):
        self.create_post('Deporte', 'deporte', '2026-10-01T12:00:00Z', 'deportes')
        self.create_post('Comida', 'comida', '2026-10-02T12:00:00Z', 'comida')

        response = self.client.get(reverse('blog:index'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['categories']), ['deportes', 'comida', 'desarrollo web', 'gaming'])
        self.assertContains(response, 'Deporte')
        self.assertContains(response, 'Comida')
        self.assertContains(response, 'id="categoria-deportes"')
        self.assertContains(response, 'id="categoria-comida"')

    def test_post_category_is_required(self):
        self.assertIn('category', [field.name for field in Post._meta.fields])
        self.assertEqual(
            Post._meta.get_field('category').choices,
            [
                ('deportes', 'Deportes'),
                ('comida', 'Comida'),
                ('desarrollo web', 'Desarrollo web'),
                ('gaming', 'Gaming'),
            ],
        )

    def test_detail_accepts_a_comment_for_that_post(self):
        post = self.create_post('Mi entrada', 'mi-entrada', '2026-10-01T12:00:00Z')

        detail_response = self.client.get(post.get_absolute_url())
        self.assertEqual(detail_response.status_code, 200)
        self.assertTemplateUsed(detail_response, 'blog/blog.html')
        self.assertContains(detail_response, 'src="/media/img/imagen.jpg"')
        self.assertContains(detail_response, '<img class="article-image"')

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

    def test_detail_embeds_video_media(self):
        post = self.create_post('Video', 'video', '2026-10-01T12:00:00Z')
        post.media = 'img/video.mp4'
        post.save()

        response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<video class="article-video" controls')
        self.assertContains(response, 'type="video/mp4"')

    def test_only_staff_can_open_post_creation_in_admin(self):
        response = self.client.get('/admin/blog/post/add/')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_superuser_sees_admin_link_from_the_blog(self):
        admin = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(admin)

        response = self.client.get(reverse('blog:index'))

        self.assertContains(response, 'Administrar publicaciones')
        self.assertContains(response, '/admin/blog/post/')

    def test_superuser_can_delete_a_comment_from_the_blog(self):
        post = self.create_post('Mi entrada', 'mi-entrada', '2026-10-01T12:00:00Z')
        comment = Comment.objects.create(
            post=post,
            author_name='Valeria',
            body='Comentario para borrar',
        )
        admin = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(admin)

        detail_response = self.client.get(post.get_absolute_url())
        response = self.client.post(
            reverse('blog:delete_comment', kwargs={'comment_id': comment.pk}),
        )

        self.assertContains(detail_response, 'Eliminar comentario de Valeria')
        self.assertRedirects(response, f'{post.get_absolute_url()}#comentarios')
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_non_admin_cannot_delete_a_comment(self):
        post = self.create_post('Mi entrada', 'mi-entrada', '2026-10-01T12:00:00Z')
        comment = Comment.objects.create(
            post=post,
            author_name='Valeria',
            body='Comentario protegido',
        )

        response = self.client.post(
            reverse('blog:delete_comment', kwargs={'comment_id': comment.pk}),
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())

    def test_comment_deletion_requires_post(self):
        post = self.create_post('Mi entrada', 'mi-entrada', '2026-10-01T12:00:00Z')
        comment = Comment.objects.create(
            post=post,
            author_name='Valeria',
            body='Comentario protegido',
        )
        admin = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(admin)

        response = self.client.get(
            reverse('blog:delete_comment', kwargs={'comment_id': comment.pk}),
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())

    def test_authenticated_user_can_like_and_unlike_a_post(self):
        post = self.create_post('Post con like', 'post-con-like', '2026-10-01T12:00:00Z')
        user = get_user_model().objects.create_user(
            username='lector',
            email='lector@example.com',
            password='test-password',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('blog:toggle_post_like', args=[post.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])
        self.assertEqual(response.json()['likes_count'], 1)
        self.assertTrue(PostLike.objects.filter(post=post, user=user).exists())

        response = self.client.post(reverse('blog:toggle_post_like', args=[post.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['liked'])
        self.assertEqual(response.json()['likes_count'], 0)
        self.assertFalse(PostLike.objects.filter(post=post, user=user).exists())

    def test_anonymous_user_cannot_like_a_post(self):
        post = self.create_post('Post protegido', 'post-protegido', '2026-10-01T12:00:00Z')

        response = self.client.post(reverse('blog:toggle_post_like', args=[post.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])
        self.assertFalse(PostLike.objects.exists())

    def test_authenticated_user_can_like_and_unlike_a_comment(self):
        post = self.create_post('Post con comentario', 'post-con-comentario', '2026-10-01T12:00:00Z')
        comment = Comment.objects.create(
            post=post,
            author_name='Valeria',
            body='Comentario interesante',
        )
        user = get_user_model().objects.create_user(
            username='lector2',
            email='lector2@example.com',
            password='test-password',
        )
        self.client.force_login(user)

        response = self.client.post(reverse('blog:toggle_comment_like', args=[comment.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])
        self.assertEqual(response.json()['likes_count'], 1)
        self.assertTrue(CommentLike.objects.filter(comment=comment, user=user).exists())

        response = self.client.post(reverse('blog:toggle_comment_like', args=[comment.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['liked'])
        self.assertEqual(response.json()['likes_count'], 0)
        self.assertFalse(CommentLike.objects.filter(comment=comment, user=user).exists())

    def test_like_unique_constraints_prevent_duplicates(self):
        post = self.create_post('Post único', 'post-unico', '2026-10-01T12:00:00Z')
        user = get_user_model().objects.create_user(
            username='lector3',
            email='lector3@example.com',
            password='test-password',
        )
        PostLike.objects.create(post=post, user=user)

        with self.assertRaises(Exception):
            PostLike.objects.create(post=post, user=user)

    def test_blog_order_can_sort_posts_by_newest_oldest_and_likes(self):
        old_post = self.create_post('Más viejo', 'mas-viejo', '2026-09-01T12:00:00Z')
        new_post = self.create_post('Más nuevo', 'mas-nuevo', '2026-10-01T12:00:00Z')
        user = get_user_model().objects.create_user(
            username='lector4',
            email='lector4@example.com',
            password='test-password',
        )
        PostLike.objects.create(post=old_post, user=user)

        newest = self.client.get(reverse('blog:index'), {'order': 'newest'})
        oldest = self.client.get(reverse('blog:index'), {'order': 'oldest'})
        liked = self.client.get(reverse('blog:index'), {'order': 'most_liked'})

        self.assertEqual(list(newest.context['posts'])[:1], [new_post])
        self.assertEqual(list(oldest.context['posts'])[:1], [old_post])
        self.assertEqual(list(liked.context['posts'])[:1], [old_post])
