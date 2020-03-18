from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Article

@shared_task
def popular_articles_update():
    all_articles = Article.objects.all()
    for article in all_articles:
        article.update_most_popular()
        print(article.popular_evaluation)
    Article.objects.bulk_update(all_articles, ['popular_evaluation'])

@shared_task
def add(x, y):
    return x + y
