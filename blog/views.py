from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import JsonResponse, Http404, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Category, Article, Comment, Tag
from .forms import CommentForm, ArticleForm

def index(request):
    #blog homepage
    article_list = Article.objects.all().order_by('-created_time')[:5]
    return render(request, 'blog/index.html', {
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
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            print(article.is_public)
            article.author = request.user
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
    data['tag_list'] = []

    if tag_name:
        tags = Tag.objects.filter(tag_name__icontains=tag_name)
        data['tag_list'] = [{'tag_id': tag.id, 'tag_name': tag.name } for tag in tags]

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

    if request.method == 'POST':
        print(request.POST)
        form = ArticleForm(request.POST, instance=article)

        if form.is_valid():
            form.save()

            return redirect('blog:my_articles')
    else:
        form = ArticleForm(instance=article)

    return render(request, 'blog/article_new.html', {
        'form': form,
    })

@login_required
def article_delete(request, article_pk):
    pass
