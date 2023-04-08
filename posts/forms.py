from django import forms
from django.db import models
from .models import Post, Group

class PostForm(forms.ModelForm):   
    text = forms.CharField(widget= forms.Textarea, label='Введите текст', help_text='Любую абракадабру') 
    group = forms.ModelChoiceField( 
        queryset=Group.objects.all(), required=False, label = 'Выберите группу', help_text='Из уже существующих' 
        ) 
    class Meta(): 
        model = Post
        fields = ['text', 'group']