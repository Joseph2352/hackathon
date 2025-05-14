from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

from Post.models import Post

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
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        else:
            # Créer l'utilisateur
            user = CustomUser.objects.create_user(
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
        user = CustomUser.objects.get(verification_code=code)
        if user.token_expiration and user.token_expiration > timezone.now():
            user.is_active = True
            user.verification_code = None
            user.token_expiration = None
            user.save()
            messages.success(request, "Votre compte a été activé avec succès ! Vous pouvez maintenant vous connecter.")
            return redirect('login')
        else:
            messages.error(request, "Le code de vérification a expiré. Veuillez demander un nouveau code.")
            return redirect('signup')
    except CustomUser.DoesNotExist:
        messages.error(request, "Code de vérification invalide.")
        return redirect('signup')


@login_required
def profil_view(request):
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'comptes/profil.html', {'user': request.user, 'posts': posts})

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
