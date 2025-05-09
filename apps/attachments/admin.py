from django.contrib import admin
from .models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ["file", "uploaded_by", "uploaded_at", "content_type", "object_id"]
    list_filter = ["uploaded_at", "content_type"]
