from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Comment, Like, Notification, Publication, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profil commune", {"fields": ("role", "bio", "avatar")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("role",)}),
    )


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "author", "is_published", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "content")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "publication", "author", "is_visible", "created_at")
    list_filter = ("is_visible", "created_at")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "publication", "created_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "notification_type", "message", "read_at", "created_at")
    list_filter = ("notification_type", "read_at")
