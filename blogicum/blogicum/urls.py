from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from blogicum import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('blog.auth_urls')),
    path('', include('blog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Добавь эту строку

handler403 = 'blogicum.views.csrf_failure'
handler404 = 'blogicum.views.page_not_found'
handler500 = 'blogicum.views.server_error'