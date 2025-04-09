from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "course", "user", "rating", "created_at"]
    list_filter = ["rating", "created_at"]
    search_fields = ["comment", "user__username", "course__title"]
    readonly_fields = ["created_at", "updated_at"]
