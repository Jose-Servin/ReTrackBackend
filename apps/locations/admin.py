from django.contrib import admin
from . import models
from unfold.admin import ModelAdmin


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "address_line1", "city", "state", "postal_code", "country"]
