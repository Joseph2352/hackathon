from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('verify-email/<str:code>/', views.verify_email, name='verify_email'),
    
    # Profil et paramètres
    path('profile/', views.profile_view, name='profile'),
    path('modifier-profil/', views.modifier_profil_view, name='modifier_profil'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='comptes/password_reset.html',
        email_template_name='comptes/password_reset_email.html',
        subject_template_name='comptes/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='comptes/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='comptes/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='comptes/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Signalements
    path('reports/create/', views.create_report, name='create_report'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/vote/', views.vote_report, name='vote_report'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    
    # Dashboard admin
    path('dashboard/', views.dashboard, name='dashboard'),
] 