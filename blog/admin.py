from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'digest', 'created_time', 'updated_time', 'is_public']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
