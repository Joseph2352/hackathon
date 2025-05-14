from django.urls import path
from .views import signup_view, login_view, logout_view, verification_sent, verify_email, profil_view, modifier_profil_view
from . import views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('verification-sent/', verification_sent, name='verification_sent'),
    path('verify-email/<str:code>/', verify_email, name='verify_email'),
    path('profil/', profil_view, name='profil'),
    path('profil/modifier/', modifier_profil_view, name='modifier_profil'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
] 