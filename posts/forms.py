from django import forms
from .models import Post, Group, Comment

class PostForm(forms.ModelForm):   
    text = forms.CharField(widget=forms.Textarea, label='Введите текст', help_text='Любую абракадабру') 
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(), required=False, label='Выберите группу', help_text='Из уже существующих'
    )

    class Meta():
        model = Post
        fields = ['text', 'group', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Напишите ваш комментарий здесь...'}),
        }
