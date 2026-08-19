from django.contrib import admin

from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'location', 'aspect', 'published', 'sort_order')
    list_filter = ('category', 'aspect', 'published')
    search_fields = ('title', 'location', 'description')
    ordering = ('sort_order', '-created_at')
