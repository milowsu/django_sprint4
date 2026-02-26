from django import forms
from .models import Post
from .models import Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'image', 'pub_date', 'is_published']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
            'category': 'Категория',
            'image': 'Изображение',
            'pub_date': 'Дата публикации',
            'is_published': 'Опубликовано',
        }
        help_texts = {
            'pub_date': 'Если указать дату в будущем - пост будет отложен',
            'is_published': 'Снимите галочку, чтобы скрыть пост',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Текст комментария',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

class ProfileEditForm(UserChangeForm):
    password = None  # Убираем поле для смены пароля из формы
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Логин',
            'email': 'Email',
        }