# Generated by Django 2.2.7 on 2020-03-14 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_auto_20200311_0322'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='popular_evaluation',
            field=models.BigIntegerField(default=0),
        ),
    ]