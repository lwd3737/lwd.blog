import markdown
import re
from django import template
from django.template.defaultfilters import stringfilter
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def slice_list(value, index):
    return value[index]

@register.filter(is_safe=True)
@stringfilter
def custom_markdown(value):
    content = mark_safe(markdown.markdown(value, extensions=['markdown.extensions.fenced_code',
        'markdown.extensions.tables'],
        safe_mode=True, enable_attributes=False))

    code_list = re.findall(r'<pre><code class="(.*)">', content, re.M)
    for code in code_list:
        content = re.sub(r'<pre><code class="(.*)">',
            '<pre class="line-numbers"><code class="language-{code}">'.format(code=code.lower()),
            content, 1)
    content = re.sub(r'<pre>\s?<code>',
        '<pre class="line-numbers"><code class="language-python">', content)

    return content

@register.simple_tag(takes_context=True)
def paginate(context, object_list, page_count):
    context['count'] = object_list.count
    paginator = Paginator(object_list, page_count)
    page = context['request'].GET.get('page')

    try:
        object_list = paginator.page(page)
        context['current_page'] = int(page)

    except PageNotAnInteger:
        object_list = paginator.page(1)
        context['current_page'] = 1
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)
        context['current_page'] = paginator.num_pages

    context['article_list'] = object_list
    context['last_page'] = paginator.num_pages
    context['first_page'] = 1
    return '' #이것을 추가하지 않으면 홈페이지가 표시

@register.filter
def tagToString(value):
    '''
    태그를 문자열로 변환
    '''
    return ','.join([each.get('tag_name', '') for each in value])

@register.filter
def getTag(value):
    tag = ''
    for each in value:
        if each.get('tag_name'):
            tag = each.gee('tag_name')
            break
    return tag
