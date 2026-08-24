from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from .models import PasswordResetToken, Profile


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'expires_at', 'used', 'created_at')
    list_filter = ('used',)
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = ('display_name', 'role', 'bio', 'avatar')


class UserAdmin(DjangoUserAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
