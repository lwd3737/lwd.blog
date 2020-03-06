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
