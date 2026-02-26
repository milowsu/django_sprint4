from django.contrib import admin
from .models import Post, Category, Location, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'text', 'pub_date', 'author', 'location',
        'category', 'is_published', 'created_at'
    )
    list_editable = ('is_published', 'category')
    search_fields = ('title', 'text')
    list_filter = ('is_published', 'category', 'location')
    list_display_links = ('title',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'description', 'slug', 'is_published', 'created_at'
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'description')
    list_filter = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'post', 'created_at')
    list_display_links = ('text',)
    # list_editable = ('text',)
    search_fields = ('text', 'author__username')
    list_filter = ('created_at', 'author')
    readonly_fields = ('created_at', 'updated_at')