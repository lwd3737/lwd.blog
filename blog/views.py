from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import JsonResponse, Http404, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Category, Article, Comment, Tag
from .forms import CommentForm, ArticleForm
import json

def index(request):
    #blog homepage
    most_popular_articles = Article.objects.all().order_by('-popular_evaluation')[:3]
    most_popular_id_list = [article.id for article in most_popular_articles]

    most_popular_tags = Tag.objects.all().order_by('-use_count')[:10]

    article_list = Article.objects.exclude(pk__in=most_popular_id_list).order_by('-created_time')

    return render(request, 'blog/index.html', {
        'most_popular_articles':most_popular_articles,
        'most_popular_tags': most_popular_tags,
        'article_list': article_list,
        'source_id': 'index',
    })

def detail(request, pk):
    article = get_object_or_404(Article, pk=pk)

    print('article',article)
    if article.is_public:
        article.view_count()
    else:
        if article.author != request.user:
            raise Http404('비공개 게시물입니다.')

    return render(request, 'blog/detail.html', {
        'article': article,
    })

def comments_display(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    comments = article.comments.prefetch_related('replies').filter(is_reply=False)
    paginator = Paginator(comments, 10)
    page = request.GET.get('page')
    pagecomments = paginator.get_page(page)
    form = CommentForm()

    return render(request, 'blog/comment.html', {
        'form': form,
        'comments': comments,
        'pagecomments': pagecomments,
        'article': article,
    })

@login_required
def comment_new(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    print(request.POST)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()
            return JsonResponse({
                'user': comment.user.username,
                'text': comment.text,
                'created_time': comment.updated_time_format(),
                'comment_id': comment.id,
            })
    #Post 요청이 아닐 시 예외 처리하기

def edit_fail(message_str):
    message = {
        'fail': message_str,
    }
    return JsonResponse(message)

@login_required
def comment_edit(request, article_pk, comment_pk):

    if request.method == 'POST':
        comment = get_object_or_404(Comment, article_id=article_pk, pk=comment_pk)

        if comment.user != request.user:
            edit_fail('해당 댓글을 수정할 권한이 없습니다.')

        form = CommentForm(request.POST)
        if form.is_valid():
            updated_comment = comment
            updated_comment.text = form.cleaned_data['text']
            updated_comment.updated_flag = True
            print(updated_comment.created_time)
            try:
                updated_comment.save()
            except Exception as e:
                print('comment save error:', e)
                edit_fail('댓글을 수정할 수 없습니다.')
            else:
                data = {
                    'comment_pk': updated_comment.id,
                    'user': updated_comment.user.username,
                    'text': updated_comment.text,
                    'updated_time': updated_comment.updated_time_format(),
                }
                return JsonResponse(data)
        else:
            edit_fail('잘못된 형식입니다.')
    else:
        edit_fail('Get 요청으로 댓글을 수정할 수 없습니다.')

@login_required
def comment_delete(request, article_pk, comment_pk):

    if request.method == 'POST':
        article = get_object_or_404(Article, pk=article_pk)
        comment = article.comments.get(pk=comment_pk, user=request.user)
        comment_id = comment.id
        try:
            comment.delete()
        except Exception as e:
            print('에러가 발생했습니다.', e)
        else:
            data = {
                'comment_id':comment_id,
            }
            return JsonResponse(data)

@login_required
def comment_reply_new(request, article_pk, comment_pk):
    comment = get_object_or_404(Comment, article__id=article_pk, pk=comment_pk)
    print(request.POST)

    if request.method == 'POST':
        context = {}
        target_reply_id = request.POST.get('target_reply_id', None)

        if target_reply_id:
            target_reply = get_object_or_404(Comment, pk=target_reply_id)

            if target_reply:
                target_user_name = target_reply.user.username
                context['target_user_name'] = target_user_name

        if target_reply_id:
            context['target_reply_id'] = target_reply_id


        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.article_id = article_pk
            reply.parent = comment
            reply.user = request.user
            reply.is_reply = True
            reply.save()

            context.update({
                'comment_id': reply.parent.id,
                'reply_id':reply.id,
                'user':reply.user.username,
                'text':reply.text,
                'created_time':reply.updated_time_format(),
            })

            return JsonResponse(context)

@login_required
def comment_reply_edit(request, article_pk, comment_pk, reply_pk):

    if request.method == 'POST':
        print(Article.objects.get(pk=article_pk))
        print(Comment.objects.get(article_id=article_pk, pk=comment_pk))
        print(Comment.objects.get(article_id=article_pk, parent_id=comment_pk,
                pk=reply_pk))
        reply = get_object_or_404(Comment, article_id=article_pk, parent_id=comment_pk,
            pk=reply_pk)

        if reply.user != request.user:
            edit_fail('해당 댓글을 수정할 권한이 없습니다.')

        form = CommentForm(request.POST)
        if form.is_valid():
            updated_reply = reply
            updated_reply.text = form.cleaned_data['text']
            updated_reply.updated_flag = True
            try:
                updated_reply.save()
            except Exception as e:
                print('comment save error:', e)
                edit_fail('댓글을 수정할 수 없습니다.')
            else:
                data = {
                    'comment_id': updated_reply.parent_id,
                    'reply_id': updated_reply.id,
                    'user': updated_reply.user.username,
                    'text': updated_reply.text,
                    'updated_time': updated_reply.updated_time_format(),
                }
                return JsonResponse(data)
        else:
            edit_fail('잘못된 형식입니다.')
    else:
        edit_fail('Get 요청으로 댓글을 수정할 수 없습니다.')

@login_required
def comment_reply_delete(request, article_pk, comment_pk, reply_pk):
    if request.method == 'POST':
        article = get_object_or_404(Article, pk=article_pk)
        comment = article.comments.get(pk=comment_pk)
        reply = comment.replies.get(pk=reply_pk, user=request.user)
        reply_id = reply.id

        try:
            reply.delete()
        except Exception as e:
            print('에러가 발생했습니다.', e)
        else:
            print('comment id:{}, reply id:{}'.format(comment.id, reply.id))
            data = {
                'comment_id':comment.id,
                'reply_id': reply_id,
            }
            return JsonResponse(data)

@login_required
def article_new(request):
    if request.method == 'POST':
        print('body data:', request.body)
        data = json.loads(request.body.decode('utf-8'))
        print('역직렬화 data:', data)
        tag_qs = []
        exist_tags = []
        created_tags = []
        tags = data['tags']
        print('tags:',tags)
        if tags:
            for tag in tags:
                if tag['id']:
                    exist_tags.append(tag['id'])
                else:
                    created_tags.append(Tag(tag_name=tag['name']))
        if exist_tags:
            tag_qs.extend(Tag.objects.filter(pk__in=exist_tags))
        if created_tags:
            created_tags_name = [tag.tag_name for tag in Tag.objects.bulk_create(created_tags)]
            created_tags_qs = Tag.objects.filter(tag_name__in=created_tags_name)
            tag_qs.extend(created_tags_qs)
        print('exist:', exist_tags, 'created:', created_tags)
        print('tag_qs:',tag_qs)
        print('tag_qs:',tag_qs)
        form = ArticleForm(data=data)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            if tag_qs:
                article.tags.set(tag_qs)
                print(article.tags.all())
                article.tags_count()
            if data['is_public'] == 'true':
                article.is_public = True
            else:
                article.is_public = False

            article.save()

            return HttpResponse(reverse('blog:my_articles'))

    else:
        form = ArticleForm()

    return render(request, 'blog/article_new.html', {
        'form':form,
    })

def tag_search(request):
    print(request.GET)
    tag_name = request.GET.get('tag_name')
    data = {}

    if tag_name:
        tag = Tag.objects.filter(tag_name=tag_name)
        print(tag)

        if tag:
            tag = tag[0]
            tag_data = {'tag_id':tag.id, 'tag_name':tag.tag_name, 'count':tag.use_count}
            data['tag'] = tag_data
        related_tags = Tag.objects.filter(tag_name__icontains=tag_name).exclude(tag_name=tag_name).order_by('-use_count')
        related_tags_data = [{'tag_id': tag.id, 'tag_name': tag.tag_name, 'count':tag.use_count } for tag in related_tags]
        data['related_tags'] = related_tags_data
        print(data)
    return JsonResponse(data)

@login_required
def my_articles(request):
    articles = Article.objects.filter(author__pk=request.user.pk)

    private_articles = articles.filter(is_public=False).order_by('-updated_time')
    public_articles = articles.filter(is_public=True).order_by('-updated_time')

    return render(request, 'blog/my_articles.html', {
        'private_articles':private_articles,
        'public_articles': public_articles,
    })

@login_required
def article_edit(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk, author=request.user)
    tags = article.tags.all()

    if request.method == 'POST':
        print('body data:', request.body)
        data = json.loads(request.body.decode('utf-8'))
        print('역직렬화 data:', data)
        tag_qs = []
        exist_tags = []
        created_tags = []
        tags = data['tags']
        print('tags:',tags)
        if tags:
            for tag in tags:
                if tag['id']:
                    exist_tags.append(tag['id'])
                else:
                    created_tags.append(Tag(tag_name=tag['name']))
        if exist_tags:
            tag_qs.extend(Tag.objects.filter(pk__in=exist_tags))
        if created_tags:
            created_tags_name = [tag.tag_name for tag in Tag.objects.bulk_create(created_tags)]
            created_tags_qs = Tag.objects.filter(tag_name__in=created_tags_name)
            tag_qs.extend(created_tags_qs)
        print('exist:', exist_tags, 'created:', created_tags)
        print('tag_qs:',tag_qs)
        form = ArticleForm(data=data, instance=article)

        if form.is_valid():
            article = form.save(commit=False)
            print('tag_qs id:', [tag.id for tag in tag_qs])
            if tag_qs:
                article.tags.set(tag_qs)
                print(article.tags.all())
                article.tags_count()
            if data['is_public'] == 'true':
                article.is_public = True
            else:
                article.is_public = False

            article.save()

            return HttpResponse(reverse('blog:my_articles'))
    else:
        form = ArticleForm(instance=article)
        print(tags)

    return render(request, 'blog/article_new.html', {
        'form': form,
        'tags': tags,
    })

@login_required
def article_delete(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk, author=request.user)

    if request.method == 'POST':
        article.delete()
        return redirect('blog:my_articles')

def articles_by_tag(request, tag_pk):
    tag = get_object_or_404(Tag, pk=tag_pk)
    articles = Article.objects.filter(tags__id=tag_pk, is_public=True).order_by('-created_time')

    return render(request, 'blog/articles_by_search.html', {
        'title':'#' + tag.tag_name,
        'articles': articles,
    })

def more_tags(request):
    tags = Tag.objects.all().order_by('-use_count')[3:]

    return render(request, 'blog/more_tags.html', {
        'tags':tags,
    })

def search(request):
    word = request.GET.get('word')

    if word:
        articles = Article.objects.filter(Q(is_public=True) & Q(title__icontains=word) | Q(content__icontains=word)
            | Q(tags__tag_name__icontains=word))
    else:
        articles = None

    return render(request, 'blog/articles_by_search.html', {
        'title': '검색결과',
        'articles': articles,
    })
