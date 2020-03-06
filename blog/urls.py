
from django.shortcuts import render
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('index/', views.index, name='index'),
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
    path('article/<int:pk>/', views.article, name='article'),
    #path('about/', views.about, name='about'),
    #path('archive', views.archive, name='archive'),
    #path('link', views.link, name='link'),
    #path('message', views.message, name='message'),
    #path('getComment/', views.getComment, name='getComment'),
    #path('search/', views.search, name='search'),
    #path('tag/', views.tag, name='tag'),
]
