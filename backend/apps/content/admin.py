from django.contrib import admin

from .models import Category, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'featured', 'published', 'published_at')
    list_filter = ('category', 'featured', 'published')
    search_fields = ('title', 'excerpt')
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_at'
