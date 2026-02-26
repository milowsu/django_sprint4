from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, ProfileEditForm
from .utils import paginate_queryset, filter_posts_by_visibility


def index(request):
    # Получаем все посты и применяем фильтр видимости
    posts = Post.objects.all()
    visible_posts = filter_posts_by_visibility(posts, request.user)
    
    page_obj = paginate_queryset(request, visible_posts)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'index.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Проверяем, может ли пользователь видеть этот пост
    if post.author == request.user:
        # Автор видит всё
        pass
    elif not (post.is_published and post.pub_date <= timezone.now()):
        # Остальные видят только опубликованные
        raise Http404("Пост не найден")
    
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comment_form': comment_form,
    }
    return render(request, 'post_detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    # Получаем посты категории и применяем фильтр
    category_posts = Post.objects.filter(category=category)
    visible_posts = filter_posts_by_visibility(category_posts, request.user)
    
    page_obj = paginate_queryset(request, visible_posts)
    
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
    profile_user = get_object_or_404(User, username=username)
    
    # Получаем посты пользователя
    user_posts = Post.objects.filter(author=profile_user)
    
    # Применяем фильтр видимости (если смотрим чужой профиль - видим только опубликованные)
    visible_posts = filter_posts_by_visibility(user_posts, request.user)
    
    page_obj = paginate_queryset(request, visible_posts)
    
    context = {
        'profile': profile_user,
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
        'is_edit': True,
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
        'post': comment.post,
    }
    return render(request, 'blog/edit_comment.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
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
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


@login_required
def edit_profile(request, username):
    user = get_object_or_404(User, username=username)
    
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