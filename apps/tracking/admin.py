from django.contrib import admin
from . import models
from unfold.admin import ModelAdmin


@admin.register(models.GPSDevice)
class GPSDeviceAdmin(admin.ModelAdmin):
    list_display = [
        "device_id",
        "assigned_vehicle",
        "is_active",
        "last_seen",
        "created_at",
    ]


@admin.register(models.GPSTrackingPing)
class GPSTrackingPingAdmin(ModelAdmin):
    list_display = [
        "gps_device",
        "latitude",
        "longitude",
        "timestamp",
        "speed_mph",
        "heading",
        "created_at",
    ]


@admin.register(models.GPSTrackingEvent)
class GPSTrackingEventAdmin(ModelAdmin):
    list_display = [
        "gps_device",
        "vehicle",
        "shipment",
        "event_type",
        "event_timestamp",
        "location",
        "note",
        "created_at",
    ]
