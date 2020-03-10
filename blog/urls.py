
from django.shortcuts import render
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('detail/<int:article_pk>/comments_display/', views.comments_display, name='comments_display'),
    path('detail/<int:article_pk>/comment/new/', views.comment_new, name='comment_new'),
    path('detail/<int:article_pk>/comment/<int:comment_pk>/delete/', views.comment_delete,
        name='comment_delete'),
    path('detail/<int:article_pk>/comment/<int:comment_pk>/edit/', views.comment_edit,
        name='comment_edit'),
    #path(detail/<int:pk>/comment/like/, views.comment_like, name='comment_like'),
    path('detail/<int:article_pk>/comment/<int:comment_pk>/reply/new/',
        views.comment_reply_new, name='comment_reply_new'),
    path('detail/<int:article_pk>/comment/<int:comment_pk>/reply/<int:reply_pk>/edit/',
        views.comment_reply_edit, name='comment_reply_edit'),
    path('detail/<int:article_pk>/comment/<int:comment_pk>/reply/<int:reply_pk>/delete/',
        views.comment_reply_delete, name='comment_reply_delete'),
    path('article/new/', views.article_new, name='article_new'),
    path('tag/search/', views.tag_search, name='tag_search'),
    path('my_articles/', views.my_articles, name='my_articles'),
    path('detail/<int:article_pk>/edit/', views.article_edit, name='article_edit'),
    path('detail/<int:article_pk>/delete/', views.article_delete, name='article_delete'),
    #path('search/', views.search, name='search'),
    #path('tag/', views.tag, name='tag'),
]
