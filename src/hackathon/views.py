from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from Post.models import Post

def home(request):
    posts = Post.objects.all().order_by('-nb_votes', '-created_at')
    context = {
        'title': 'Accueil - Votre Site Professionnel',
        'meta_description': 'Bienvenue sur notre site professionnel. Découvrez nos services et notre expertise.',
        'meta_keywords': 'accueil, professionnel, services, expertise',
        'posts': posts,
    }
    return render(request, 'hackathon/home.html', context)

def about(request):
    context = {
        'title': 'À Propos - Votre Site Professionnel',
        'meta_description': 'Découvrez notre histoire, notre mission et notre équipe.',
        'meta_keywords': 'à propos, histoire, mission, équipe',
    }
    return render(request, 'hackathon/about.html', context)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Préparation du message
        email_subject = f'Nouveau message de contact - {subject}'
        email_message = f"""
        Nouveau message de contact reçu :

        Nom : {name}
        Email : {email}
        Sujet : {subject}

        Message :
        {message}
        """

        try:
            # Envoi de l'email
            send_mail(
                email_subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],  # À configurer dans settings.py
                fail_silently=False,
            )
            messages.success(request, 'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.')
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors de l\'envoi du message. Veuillez réessayer plus tard.')

    context = {
        'title': 'Contact - Votre Site Professionnel',
        'meta_description': 'Contactez-nous pour toute question ou demande d\'information.',
        'meta_keywords': 'contact, information, demande, support',
    }
    return render(request, 'hackathon/contact.html', context) 