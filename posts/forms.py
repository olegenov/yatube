from django import forms
from django.forms import ModelForm, Textarea

from .models import Post, Comment, ProfilePhoto


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        widgets = {
            'text': Textarea(attrs={'cols': 50, 'rows': 10}),
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={'cols': 80, 'rows': 3}),
        }

class ProfilePhotoForm(ModelForm):
    class Meta:
        model = ProfilePhoto
        fields = ['photo']
