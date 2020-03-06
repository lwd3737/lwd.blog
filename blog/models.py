from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(verbose_name='카테고리', max_length=30)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = '카테고리'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey('Category', verbose_name='카테고리', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    digest = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    view = models.BigIntegerField(default=0)
    claps = models.BigIntegerField(default=0)
    picture = models.CharField(max_length=200, blank=True, null=True)  #타이틀 이미지 주소
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_time']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', args=(self.id,))

    def view_count(self):
        self.view += 1  #race condition
        self.save(update_fields=['view'])

    def claps(self):
        self.claps += 1
        self.save(update_fields=['claps'])


class Tag(models.Model):
    tag_name = models.CharField(verbose_name='태그 이름',max_length=30)

    def __str__(self):
        return self.tag_name

class CommentManager(models.Manager):
    def replies_order_by(self):
        return self.all().order_by('created_time')

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies',
        null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    text = models.CharField(max_length=4000)
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)
    updated_flag = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    objects = CommentManager()

    class Meta:
        ordering = ['-created_time']

    def __str__(self):
        return self.user.username + '의 댓글 id {}'.format(self.id)

    def updated_time_format(self):
        if self.updated_flag:
            return '(수정됨)' + self.updated_time.strftime('%Y-%m-%d %H:%M')
        return self.created_time.strftime('%Y-%m-%d %H:%M')

class CommentReply(Comment):
    class Meta:
        proxy = True
        ordering = ['created_time']
