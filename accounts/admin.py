from django.contrib import admin
from .models import User

@admin.register(User)
class UserAmdin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_superuser', 'is_active',)
    list_display_links= ('id', 'username')
    exclude = ('password',)
