from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, ProfileEditForm

def index(request):
    post_list = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'index.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if not post.is_published and post.author != request.user:
        raise Http404("Пост не найден")
    
    comment_form = CommentForm()  # Добавь форму в контекст
    
    context = {
        'post': post,
        'comment_form': comment_form,  # Добавь это
    }
    return render(request, 'post_detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    post_list = Post.objects.filter(category=category)
    paginator = Paginator(post_list, 10)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'category.html', context)
class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
def about(request):
    return render(request, 'pages/about.html')

def rules(request):
    return render(request, 'pages/rules.html')

def profile(request, username):
    user = get_object_or_404(User, username=username)
    
    # Получаем все посты пользователя
    post_list = Post.objects.filter(author=user)
    
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, 'profile.html', context)
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('profile', username=request.user.username)
    else:
        form = PostForm()
    
    context = {'form': form}
    return render(request, 'blog/create_post.html', context)
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Проверяем, что пользователь - автор поста
    if post.author != request.user:
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'is_edit': True,  # Флаг для шаблона, чтобы знать что это редактирование
    }
    return render(request, 'blog/create_post.html', context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)
    return redirect('post_detail', post_id=post.id)

@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    
    # Проверяем, что пользователь - автор комментария
    if comment.author != request.user:
        return redirect('post_detail', post_id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    
    context = {
        'form': form,
        'comment': comment,
        'post': comment.post,  # Вот это было исправлено!
    }
    return render(request, 'blog/edit_comment.html', context)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Проверяем, что пользователь - автор поста
    if post.author != request.user:
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        post.delete()
        return redirect('profile', username=request.user.username)
    
    context = {
        'post': post,
    }
    return render(request, 'blog/delete_post.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    
    # Проверяем, что пользователь - автор комментария
    if comment.author != request.user:
        return redirect('post_detail', post_id=post_id)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('post_detail', post_id=post_id)
    
    context = {
        'comment': comment,
        'post': comment.post,
    }
    return render(request, 'blog/delete_comment.html', context)

class AboutView(TemplateView):
    """Страница "О проекте" """
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Страница "Наши правила" """
    template_name = 'pages/rules.html'

@login_required
def edit_profile(request, username):
    user = get_object_or_404(User, username=username)
    
    # Проверяем, что пользователь редактирует свой профиль
    if user != request.user:
        return redirect('profile', username=username)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=user.username)
    else:
        form = ProfileEditForm(instance=user)
    
    context = {
        'form': form,
        'profile': user,
    }
    return render(request, 'blog/edit_profile.html', context)