from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, F, Q, Case, When, Value, CharField
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.models import User
from .models import Post, Vote
from .forms import PostForm
from django.http import JsonResponse
from django.contrib import messages
from comptes.models import CustomUser
from django.db.models.functions import TruncDate
import json

# Create your views here.

def posts(request):
  posts = Post.objects.all().annotate(votes_count=Count('vote'))
  return render(request, 'Post/posts.html', {'posts': posts})

def post_detail(request, pk):
  post = Post.objects.annotate(votes_count=Count('vote')).get(pk=pk)
  return render(request, 'Post/post_detail.html', {'post': post})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.user = request.user
                post.status = 'pending'  # Statut initial
                post.created_at = timezone.now()
                
                # Validation des coordonnées
                latitude = form.cleaned_data.get('latitude')
                longitude = form.cleaned_data.get('longitude')
                
                if latitude is None or longitude is None:
                    messages.error(request, 'Veuillez sélectionner une position sur la carte.')
                    return render(request, 'Post/post_create.html', {
                        'form': form,
                        'user': request.user
                    })
                
                # Validation des coordonnées (Paris)
                if not (48.8 <= latitude <= 48.9) or not (2.2 <= longitude <= 2.5):
                    messages.warning(request, 'La position sélectionnée semble être en dehors de Paris.')
                
                post.save()
                messages.success(request, 'Votre signalement a été publié avec succès !')
                return redirect('post_detail', pk=post.pk)
            except Exception as e:
                messages.error(request, f'Une erreur est survenue lors de la création du signalement : {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erreur dans le champ {field}: {error}')
    else:
        form = PostForm()
    
    return render(request, 'Post/post_create.html', {
        'form': form,
        'user': request.user,
        'default_latitude': 48.8566,  # Coordonnées par défaut (Paris)
        'default_longitude': 2.3522
    })

def post_update(request, pk):
  post=Post.objects.get(pk=pk)
  if request.method == 'POST':
    form=PostForm(request.POST, request.FILES, instance=post)
    if form.is_valid():
      form.save()
      return redirect('post_detail', pk=pk)
  else:
    form=PostForm(instance=post)  
  return render(request, 'hackathon/post_update.html', {'form': form})

def post_delete(request, pk):
  post=Post.objects.get(pk=pk)
  post.delete()
  return redirect('posts')

def post_vote(request, pk):
    post = Post.objects.get(pk=pk)
    user = request.user
    voted = False
    if request.method == 'POST':
        try:
            vote = Vote.objects.get(post=post, user=user)
            vote.delete()
            voted = False
        except Vote.DoesNotExist:
            Vote.objects.create(post=post, user=user)
            voted = True
    votes_count = Vote.objects.filter(post=post).count()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'votes_count': votes_count, 'voted': voted})
    return redirect('post_detail', pk=pk)

@login_required
def dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('home')
    
    # Statistiques générales
    total_posts = Post.objects.count()
    total_users = CustomUser.objects.count()
    
    # Statistiques des posts par catégorie
    posts_by_category = Post.objects.values('category').annotate(count=Count('id'))
    
    # Statistiques des posts par statut
    posts_by_status = Post.objects.values('status').annotate(count=Count('id'))
    
    # Statistiques des posts par date (7 derniers jours)
    seven_days_ago = timezone.now() - timedelta(days=7)
    posts_by_date = Post.objects.filter(created_at__gte=seven_days_ago).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    # Utilisateurs actifs (ayant créé au moins un post)
    active_users = CustomUser.objects.filter(
        posts__isnull=False
    ).distinct().count()
    
    # Posts récents
    recent_posts = Post.objects.select_related('user').order_by('-created_at')[:5]
    
    # Posts en attente de modération
    pending_posts = Post.objects.filter(status='attente').select_related('user')
    
    context = {
        'total_posts': total_posts,
        'total_users': total_users,
        'active_users': active_users,
        'posts_by_category': list(posts_by_category),
        'posts_by_status': list(posts_by_status),
        'posts_by_date': list(posts_by_date),
        'recent_posts': recent_posts,
        'pending_posts': pending_posts,
    }
    
    return render(request, 'Post/dashboard.html', context)

@login_required
def map_view(request):
    # Récupérer tous les signalements avec leurs coordonnées
    posts_for_map = Post.objects.values(
        'id', 'title', 'description', 'latitude', 'longitude', 
        'category', 'status', 'created_at'
    ).order_by('-created_at')
    
    # Convertir les dates en format string pour la sérialisation JSON
    posts_list = []
    for post in posts_for_map:
        post_dict = dict(post)
        post_dict['created_at'] = post_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        posts_list.append(post_dict)
    
    # Convertir en JSON pour le JavaScript
    posts_data = json.dumps(posts_list)

    context = {
        'posts_data': posts_data,
    }

    return render(request, 'Post/map_view.html', context)
