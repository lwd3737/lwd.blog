from __future__ import absolute_import, unicode_literals
from celery import shared_task
from bs4 import BeautifulSoup
from .models import Article, News
import requests

@shared_task
def popular_articles_update():
    all_articles = Article.objects.all()
    for article in all_articles:
        article.update_most_popular()
        print(article.popular_evaluation)
    Article.objects.bulk_update(all_articles, ['popular_evaluation'])

@shared_task
def corona_news_update():
    res = requests.get('http://ncov.mohw.go.kr/')
    soup = BeautifulSoup(res.content, 'html.parser')
    today_liveNum = soup.select('ul.liveNum_today > li')
    liveNums = soup.select('ul.liveNum > li')
    data_ = {
        'today_live_num':[],
        'live_nums':[],
    }

    date = soup.select('span.livedate')[0].get_text()
    data_['live_date'] = date

    for item in today_liveNum:
        title = item.select('span')[0].get_text()
        data = item.select('span')[1].get_text()
        data_['today_live_num'].append({
            'title':title,
            'data':data,
        })

    for item in liveNums:
        title = item.select('.tit')[0].get_text()
        num = item.select('.num')[0].get_text()
        before = item.select('.before')[0].get_text()
        data_['live_nums'].append({
            'title':title,
            'num':num,
            'before':before,
        })

        news = News.objects.filter(topic='corona')
        if news:
            news = news[0]
            news.data = data_
            news.save(update_fields=['data'])
        else:
            News.objects.create(topic='corona', data=data_)
    print('Corona data update Success!:', data_)
