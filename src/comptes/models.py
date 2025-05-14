from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

# Create your models here.

class CustomUser(AbstractUser):
    # Ajoute ici des champs personnalisés si besoin
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    telephone = models.CharField(max_length=10, null=True, blank=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    date_de_naissance = models.DateField(null=True, blank=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    token_expiration = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    pass

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Profile de {self.user.username}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Report(models.Model):
    REPORT_TYPES = (
        ('spam', 'Spam'),
        ('inappropriate', 'Contenu inapproprié'),
        ('harassment', 'Harcèlement'),
        ('other', 'Autre'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    votes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='report_votes',
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'En attente'),
            ('reviewing', 'En cours d\'examen'),
            ('resolved', 'Résolu'),
            ('dismissed', 'Rejeté'),
        ),
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Signalement de {self.user.username}: {self.type}'

class ReportComment(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Commentaire de {self.user.username} sur le signalement {self.report.id}'

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('mention', 'Mention'),
        ('comment', 'Commentaire'),
        ('vote', 'Vote'),
        ('report', 'Signalement'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification pour {self.user.username}: {self.type}'
