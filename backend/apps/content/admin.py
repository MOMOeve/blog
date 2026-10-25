from django.contrib import admin

from .models import Category, Comment, Post, PostLike, PostViewRecord, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'featured', 'published', 'view_count', 'like_count', 'published_at')
    list_filter = ('category', 'featured', 'published')
    search_fields = ('title', 'excerpt')
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_at'
    readonly_fields = ('view_count', 'like_count')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'approved', 'created_at')
    list_filter = ('approved',)
    search_fields = ('body', 'author__username', 'post__title')
    list_editable = ('approved',)


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'visitor_id', 'created_at')
    search_fields = ('post__title', 'visitor_id')


@admin.register(PostViewRecord)
class PostViewRecordAdmin(admin.ModelAdmin):
    list_display = ('post', 'visitor_id', 'created_at')
    search_fields = ('post__title', 'visitor_id')
