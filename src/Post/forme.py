from django import forms
from .models import Post

class PostForm(forms.ModelForm):
  class Meta:
    model=Post
    fields=['title', 'description', 'image', 'latitude', 'longitude', 'category', 'status']
    widgets={
      'title': forms.TextInput(attrs={'class': 'form-control'}),
      'description': forms.Textarea(attrs={'class': 'form-control'}),
      'image': forms.FileInput(attrs={'class': 'form-control'}),
      'latitude': forms.TextInput(attrs={'class': 'form-control'}),
      'longitude': forms.TextInput(attrs={'class': 'form-control'}),
      'category': forms.Select(attrs={'class': 'form-control'}),
      'status': forms.Select(attrs={'class': 'form-control'}),
    }
