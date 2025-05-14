from django.db import models
from comptes.models import CustomUser
# Create your models here.

class Post(models.Model):
  user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
  title=models.CharField(max_length=200)
  description=models.TextField()
  image=models.ImageField(upload_to='posts', null=True, blank=True)
  created_at=models.DateTimeField(auto_now_add=True)
  latitude=models.FloatField()
  longitude=models.FloatField()
  updated_at=models.DateTimeField(auto_now=True)
  nb_votes=models.IntegerField(default=0)
  CATEGORY_CHOICES = [
    ('route', 'Route endommagée'),
    ('electricite', 'Panne électrique'),
    ('dechets', 'Déchets non collectés'),
    ('autre', 'Autre'),
  ]
  STATUS_CHOICES = [
    ('attente', 'En attente'),
    ('encours', 'En cours'),
    ('resolu', 'Résolu'),
  ]
  category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='autre')
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='attente')

  def __str__(self):
    return self.title

class Vote(models.Model):
  post=models.ForeignKey(Post, on_delete=models.CASCADE)
  vote=models.BooleanField(default=True)
  user=models.ForeignKey(CustomUser, on_delete=models.CASCADE, unique=True)

  def __str__(self):
    return f"{self.user.username} voted {self.vote} for {self.post.title}"
