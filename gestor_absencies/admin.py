from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Worker


class CustomUserAdmin(UserAdmin):
    model = Worker
    list_display = ['email', 'username']


admin.site.register(Worker, CustomUserAdmin)
