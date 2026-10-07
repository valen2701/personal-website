from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<slug:slug>/', views.detail, name='detail'),
]
