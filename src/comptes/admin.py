from django.contrib import admin
from .models import CustomUser

# Register your models here.
admin.site.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'telephone', 'adresse', 'date_de_naissance', 'is_active')
    list_filter = ('username', 'email', 'first_name', 'last_name', 'telephone', 'adresse', 'date_de_naissance', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'telephone', 'adresse', 'date_de_naissance')
    list_per_page = 10


