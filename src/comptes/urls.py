from django.urls import path
from .views import signup_view, login_view, logout_view, verification_sent, verify_email, profil_view, modifier_profil_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('verification-sent/', verification_sent, name='verification_sent'),
    path('verify-email/<str:code>/', verify_email, name='verify_email'),
    path('profil/', profil_view, name='profil'),
    path('profil/modifier/', modifier_profil_view, name='modifier_profil'),
] 