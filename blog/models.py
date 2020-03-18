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

    def align_category(self):
        tags = Tag.objects.all().order_by('-use_count')[:10]
        return tags

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    digest = models.CharField(max_length=200, blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    view = models.BigIntegerField(default=0)
    like = models.BigIntegerField(default=0)
    #picture = models.CharField(max_length=200, blank=True, null=True)  #타이틀 이미지 주소
    popular_evaluation = models.BigIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_time']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', args=(self.id,))

    def tags_count(self):
        tag_qs = self.tags.all()
        for tag in tag_qs:
            count = tag.use_count + 1
        tag_qs.update(use_count=count)

    def view_count(self):
        self.view += 1  #race condition
        self.save(update_fields=['view'])

    def like_count(self):
        self.like += 1
        self.save(update_fields=['like'])

    def update_most_popular(self):
        comment_count = Comment.objects.filter(article__id=self.id).count()
        self.popular_evaluation = (self.like * 3) + self.view + (comment_count * 2)

    def created_time_format(self):
        return self.created_time.strftime('%Y-%m-%d %H:%M')

    def updated_time_format(self):
        return self.updated_time.strftime('%Y-%m-%d %H:%M')

    def tags_count_sub():
        tags = self.tags.all()
        updated_tags = []

        for tag in tags:
            if tag.use_count > 0:
                tag.use_count -= 1
                updated_tags.append(tag)

        tags.objects.bulk_update(updated_tags, ['use_count'])

class Tag(models.Model):
    tag_name = models.CharField(unique=True, verbose_name='태그 이름',max_length=30)
    use_count = models.PositiveIntegerField(default=0)

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
    is_reply = models.BooleanField(default=False)
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
