from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.models import User
from .models import Post, Vote
import json
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.db.models import ExpressionWrapper, DurationField
from .forms import PostForm
from django.http import JsonResponse

# Create your views here.

def posts(request):
  posts = Post.objects.all().annotate(votes_count=Count('vote'))
  return render(request, 'Post/posts.html', {'posts': posts})

def post_detail(request, pk):
  post = Post.objects.annotate(votes_count=Count('vote')).get(pk=pk)
  return render(request, 'post_detail.html', {'post': post})

def post_create(request):
  if request.method == 'POST':
    form=PostForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      return redirect('posts')
  else:
    form=PostForm()
  return render(request, 'Post/post_create.html', {'form': form})

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
    # Période sélectionnée (par défaut: 30 derniers jours)
    period = request.GET.get('period', '30d')
    end_date = timezone.now()
    
    if period == '7d':
        start_date = end_date - timedelta(days=7)
        group_by = TruncDay('created_at')
    elif period == '30d':
        start_date = end_date - timedelta(days=30)
        group_by = TruncDay('created_at')
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
        group_by = TruncWeek('created_at')
    elif period == '1y':
        start_date = end_date - timedelta(days=365)
        group_by = TruncMonth('created_at')
    else:
        start_date = end_date - timedelta(days=30)
        group_by = TruncDay('created_at')

    # Statistiques générales
    total_posts = Post.objects.count()
    posts_this_month = Post.objects.filter(
        created_at__gte=timezone.now().replace(day=1, hour=0, minute=0, second=0)
    ).count()
    resolved_posts = Post.objects.filter(status='resolved').count()
    active_users = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=30)
    ).count()

    # Temps de résolution moyen
    resolution_time = Post.objects.filter(
        status='resolved',
        resolved_at__isnull=False
    ).annotate(
        resolution_duration=ExpressionWrapper(
            F('resolved_at') - F('created_at'),
            output_field=DurationField()
        )
    ).aggregate(
        avg_resolution_time=Avg('resolution_duration')
    )['avg_resolution_time']

    # Convertir en heures si disponible
    avg_resolution_hours = resolution_time.total_seconds() / 3600 if resolution_time else 0

    # Statistiques par catégorie
    category_stats = Post.objects.values('category').annotate(
        count=Count('id'),
        resolved_count=Count('id', filter=Q(status='resolved')),
        avg_resolution_time=Avg(
            ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=DurationField()
            ),
            filter=Q(status='resolved', resolved_at__isnull=False)
        )
    ).order_by('category')

    # Statistiques par zone (en utilisant des coordonnées approximatives)
    zone_stats = Post.objects.annotate(
        zone=Case(
            When(
                Q(latitude__gte=48.85, longitude__gte=2.35),
                then=Value('Nord-Est')
            ),
            When(
                Q(latitude__gte=48.85, longitude__lt=2.35),
                then=Value('Nord-Ouest')
            ),
            When(
                Q(latitude__lt=48.85, longitude__gte=2.35),
                then=Value('Sud-Est')
            ),
            default=Value('Sud-Ouest'),
            output_field=CharField(),
        )
    ).values('zone').annotate(
        count=Count('id'),
        resolved_count=Count('id', filter=Q(status='resolved')),
        avg_resolution_time=Avg(
            ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=DurationField()
            ),
            filter=Q(status='resolved', resolved_at__isnull=False)
        )
    ).order_by('zone')

    # Tendances temporelles
    trend_data = Post.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).annotate(
        period=group_by
    ).values('period').annotate(
        count=Count('id'),
        resolved_count=Count('id', filter=Q(status='resolved'))
    ).order_by('period')

    # Préparer les données pour les graphiques
    trend_labels = [data['period'].strftime('%d/%m/%Y' if period in ['7d', '30d'] else '%m/%Y') for data in trend_data]
    trend_counts = [data['count'] for data in trend_data]
    trend_resolved = [data['resolved_count'] for data in trend_data]

    # Données pour le graphique des catégories
    category_labels = [dict(Post.CATEGORY_CHOICES)[stat['category']] for stat in category_stats]
    category_data = [stat['count'] for stat in category_stats]
    category_resolved = [stat['resolved_count'] for stat in category_stats]

    # Données pour le graphique des zones
    zone_labels = [stat['zone'] for stat in zone_stats]
    zone_data = [stat['count'] for stat in zone_stats]
    zone_resolved = [stat['resolved_count'] for stat in zone_stats]

    context = {
        'total_posts': total_posts,
        'posts_this_month': posts_this_month,
        'resolved_posts': resolved_posts,
        'active_users': active_users,
        'avg_resolution_hours': round(avg_resolution_hours, 1),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'category_resolved': json.dumps(category_resolved),
        'zone_labels': json.dumps(zone_labels),
        'zone_data': json.dumps(zone_data),
        'zone_resolved': json.dumps(zone_resolved),
        'trend_labels': json.dumps(trend_labels),
        'trend_data': json.dumps(trend_counts),
        'trend_resolved': json.dumps(trend_resolved),
        'current_period': period,
        'periods': [
            {'value': '7d', 'label': '7 derniers jours'},
            {'value': '30d', 'label': '30 derniers jours'},
            {'value': '90d', 'label': '3 derniers mois'},
            {'value': '1y', 'label': '1 an'}
        ],
        'category_stats': category_stats,
        'zone_stats': zone_stats,
    }

    return render(request, 'Post/dashboard.html', context)

@login_required
def map_view(request):
    # Récupérer tous les signalements avec leurs coordonnées
    posts_for_map = Post.objects.values(
        'id', 'title', 'description', 'latitude', 'longitude', 
        'category', 'status', 'created_at'
    ).order_by('-created_at')
    
    # Convertir en JSON pour le JavaScript
    posts_data = json.dumps(list(posts_for_map))

    context = {
        'posts_data': posts_data,
    }

    return render(request, 'Post/map_view.html', context)
