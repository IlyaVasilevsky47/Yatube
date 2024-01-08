from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': 'Текст поста', 'group': 'Группа', 'image': 'Картинка'
        }
        widgets = {
            'text': forms.Textarea(
                attrs={'cols': '40', 'rows': '10', 'class': 'form-control'},
            ),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(
                attrs={'class': 'form-control'}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(
                attrs={'class': 'form-control', 'style': "height: 100px;"},
            ),
        }
