from django.contrib import admin
from .models import Post
# Register your models here.

admin.site.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    list_per_page = 10


