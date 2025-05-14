from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.posts, name='posts'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/update/<int:pk>/', views.post_update, name='post_update'),
    path('post/delete/<int:pk>/', views.post_delete, name='post_delete'),
    path('post/vote/<int:pk>/', views.post_vote, name='post_vote'),
]
