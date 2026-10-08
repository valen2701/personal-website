from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:post_id>/like/', views.toggle_post_like, name='toggle_post_like'),
    path('comments/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<slug:slug>/', views.detail, name='detail'),
]
