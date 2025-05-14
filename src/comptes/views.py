from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Profile, Report, ReportComment, Notification
from .forms import UserRegistrationForm, ReportForm, ProfileUpdateForm, UserUpdateForm
import json

from Post.models import Post

User = get_user_model()

# Create your views here.

# Inscription avec formulaire HTML natif

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')
        date_de_naissance = request.POST.get('date_de_naissance')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not email or not telephone or not adresse or not date_de_naissance or not password1 or not password2:
            messages.error(request, "Tous les champs sont obligatoires.")
        elif password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        else:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                telephone=telephone,
                adresse=adresse,
                date_de_naissance=date_de_naissance,
                password=password1
            )
            user.is_active = False  # Désactiver le compte jusqu'à la vérification
            user.save()

            # Générer le code de vérification
            verification_code = get_random_string(length=6, allowed_chars='0123456789')
            user.verification_code = verification_code
            user.token_expiration = timezone.now() + timezone.timedelta(minutes=10)
            user.save()

            # Préparer l'email
            subject = 'Vérification de votre compte'
            verification_link = request.build_absolute_uri(
                reverse('verify_email', args=[verification_code])
            )
            html_message = render_to_string('comptes/verification_email.html', {
                'username': username,
                'verification_code': verification_code,
                'verification_link': verification_link,
            })
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = email

            # Envoyer l'email
            try:
                send_mail(
                    subject,
                    plain_message,
                    from_email,
                    [to_email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, "Inscription réussie ! Veuillez vérifier votre email pour activer votre compte.")
                return redirect('verification_sent')
            except Exception as e:
                print(f"Erreur d'envoi d'email : {str(e)}")  # Pour voir l'erreur dans la console
                messages.error(request, f"Erreur lors de l'envoi de l'email de vérification : {str(e)}")
                user.delete()  # Supprimer l'utilisateur si l'envoi d'email échoue
                return redirect('signup')

    return render(request, 'comptes/signup.html')

# Connexion avec formulaire HTML natif

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie !")
            return redirect('home')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'comptes/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('home')

def verification_sent(request):
    return render(request, 'comptes/verification_sent.html')

def verify_email(request, code):
    try:
        user = User.objects.get(verification_code=code)
        if user.token_expiration and user.token_expiration > timezone.now():
            user.is_active = True
            user.verification_code = None
            user.token_expiration = None
            user.save()
            
            # Créer le profil associé
            Profile.objects.create(user=user)
            
            messages.success(request, "Votre compte a été activé avec succès ! Vous pouvez maintenant vous connecter.")
            return redirect('login')
        else:
            messages.error(request, "Le code de vérification a expiré. Veuillez demander un nouveau code.")
            return redirect('signup')
    except User.DoesNotExist:
        messages.error(request, "Code de vérification invalide.")
        return redirect('signup')


@login_required
def modifier_profil_view(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')
        date_de_naissance = request.POST.get('date_de_naissance')
        
        # Mettre à jour les informations de l'utilisateur
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.telephone = telephone
        user.adresse = adresse
        user.date_de_naissance = date_de_naissance
        
        # Gérer l'upload de l'image de profil
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            user.profile_picture = profile_picture
        
        user.save()
        messages.success(request, "Votre profil a été mis à jour avec succès !")
        return redirect('profil')
    
    return render(request, 'comptes/modifier_profil.html', {'user': request.user})

@login_required
def profile_view(request):
    try:
        user = request.user
        profile = user.profile
        
        if request.method == 'POST':
            user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Votre profil a été mis à jour avec succès !')
                return redirect('profile')
        else:
            user_form = UserUpdateForm(instance=user)
            profile_form = ProfileUpdateForm(instance=profile)
        
        context = {
            'user': user,
            'user_form': user_form,
            'profile_form': profile_form,
            'profile': profile,
            'posts': user.posts.all().order_by('-created_at')[:5],
            'notifications': Notification.objects.filter(user=user, is_read=False).order_by('-created_at')[:5]
        }
        return render(request, 'comptes/profile_new.html', context)
    except Exception as e:
        messages.error(request, f"Une erreur est survenue : {str(e)}")
        return redirect('home')

@login_required
def create_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            
            # Créer une notification pour les administrateurs
            admins = Profile.objects.filter(role='admin')
            for admin in admins:
                Notification.objects.create(
                    user=admin.user,
                    report=report,
                    title='Nouveau signalement',
                    message=f'Nouveau signalement créé par {request.user.username}'
                )
            
            messages.success(request, 'Signalement créé avec succès !')
            return redirect('report_detail', report_id=report.id)
    else:
        form = ReportForm()
    return render(request, 'comptes/create_report.html', {'form': form})

@login_required
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    comments = report.comments.all().order_by('-created_at')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                content=content
            )
            return redirect('report_detail', report_id=report.id)
    
    return render(request, 'comptes/report_detail.html', {
        'report': report,
        'comments': comments
    })

@login_required
def vote_report(request, report_id):
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        if request.user in report.votes.all():
            report.votes.remove(request.user)
            voted = False
        else:
            report.votes.add(request.user)
            voted = True
        
        return JsonResponse({
            'success': True,
            'votes': report.vote_count(),
            'voted': voted
        })
    return JsonResponse({'success': False}, status=400)

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = get_object_or_404(Notification, id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
    
    return render(request, 'comptes/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def dashboard(request):
    if request.user.profile.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('home')
    
    reports = Report.objects.all().order_by('-created_at')
    stats = {
        'total_reports': reports.count(),
        'pending_reports': reports.filter(status='pending').count(),
        'in_progress_reports': reports.filter(status='in_progress').count(),
        'resolved_reports': reports.filter(status='resolved').count(),
    }
    
    return render(request, 'comptes/dashboard.html', {
        'reports': reports,
        'stats': stats
    })
