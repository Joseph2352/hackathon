from django.shortcuts import render

# Create your views here.

def posts(request):
  posts=Post.objects.all()
  return render(request, 'posts.html', {'posts': posts})

def post_detail(request, pk):
  post=Post.objects.get(pk=pk)
  return render(request, 'post_detail.html', {'post': post})

def post_create(request):
  if request.method == 'POST':
    form=PostForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      return redirect('posts')
  else:
    form=PostForm()
  return render(request, 'post_create.html', {'form': form})

def post_update(request, pk):
  post=Post.objects.get(pk=pk)
  if request.method == 'POST':
    form=PostForm(request.POST, request.FILES, instance=post)
    if form.is_valid():
      form.save()
      return redirect('post_detail', pk=pk)
  else:
    form=PostForm(instance=post)  
  return render(request, 'post_update.html', {'form': form})

def post_delete(request, pk):
  post=Post.objects.get(pk=pk)
  post.delete()
  return redirect('posts')

def post_vote(request, pk):
  post=Post.objects.get(pk=pk)
  vote=Vote.objects.get(post=post, user=request.user)
  if vote:
    vote.delete()
  else:
    Vote.objects.create(post=post, user=request.user)
  post.nb_votes=Vote.objects.filter(post=post).count()
  post.save()
  return redirect('post_detail', pk=pk)
