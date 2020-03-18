from django import forms
from .models import Article, Comment

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ['text']
		widgets = {
			'text': forms.Textarea(attrs={
				'resize':'none',
				'placeholder':'댓글을 작성하세요.',
			}),
		}
		labels = {
			'text': '댓글',
		}

class ArticleForm(forms.ModelForm):
	class Meta:
		model = Article
		fields = ['title', 'content', 'digest',]
		widgets = {
			'title': forms.TextInput(attrs={'placeholder': '제목...'}),
			'content': forms.Textarea(attrs={'placeholder': '내용...', 'resize':'false'}),
			'digest': forms.TextInput(attrs={'placeholder': '요약...'}),
		}
		labels = {
			'title': '제목',
			'content': '내용',
			'digest': '요약',
			'tags': '태그',
		}
