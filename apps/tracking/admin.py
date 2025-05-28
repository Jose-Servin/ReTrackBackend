from django.contrib import admin
from . import models
from unfold.admin import ModelAdmin


@admin.register(models.GPSDevice)
class GPSDeviceAdmin(ModelAdmin):
    list_display = [
        "serial_number",
        "assigned_vehicle",
        "is_active",
        "last_seen",
        "created_at",
    ]

    list_select_related = ["assigned_vehicle", "assigned_vehicle__carrier"]


@admin.register(models.GPSTrackingPing)
class GPSTrackingPingAdmin(ModelAdmin):
    list_display = [
        "gps_device",
        "latitude",
        "longitude",
        "recorded_at",
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

    list_select_related = [
        "gps_device",
        "vehicle__carrier",
        "shipment__origin",
        "shipment__destination",
        "location",
    ]
