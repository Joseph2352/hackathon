from django.contrib.auth.models import AbstractUser
from django.db import models

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
