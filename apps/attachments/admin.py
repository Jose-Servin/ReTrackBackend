from django.contrib import admin
from unfold.admin import ModelAdmin
from . import models


@admin.register(models.Attachment)
class AttachmentAdmin(ModelAdmin):
    list_display = ["file", "uploaded_by", "uploaded_at", "content_type", "object_id"]
    list_filter = ["uploaded_at", "content_type"]
