from django.core.paginator import Paginator
from django.utils import timezone

def paginate_queryset(request, queryset, posts_per_page=10):
    """
    Универсальная функция для пагинации queryset'а.
    Возвращает page_obj для использования в шаблоне.
    """
    paginator = Paginator(queryset, posts_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def filter_posts_by_visibility(queryset, user=None):
    """
    Фильтрует посты в зависимости от прав доступа:
    - Если пользователь авторизован и является автором - видит все свои посты
    - Для остальных пользователей - только опубликованные посты с датой <= сейчас
    """
    now = timezone.now()
    
    # Базовый фильтр для всех пользователей: опубликовано и дата не в будущем
    base_filter = queryset.filter(
        is_published=True,
        pub_date__lte=now
    )
    
    # Если пользователь авторизован, добавляем его посты (даже неопубликованные)
    if user and user.is_authenticated:
        # Посты автора (без фильтрации по статусу и дате)
        author_posts = queryset.filter(author=user)
        # Объединяем через union (или можно через OR в filter)
        return base_filter | author_posts
    
    return base_filter