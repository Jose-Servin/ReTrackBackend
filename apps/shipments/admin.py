from django.contrib import admin
from . import models


@admin.register(models.Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ["name", "mc_number", "created_at", "updated_at"]


@admin.register(models.CarrierContact)
class CarrierContactAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "carrier", "role", "is_primary"]
    list_editable = ["is_primary"]
    list_select_related = ["carrier"]


@admin.register(models.Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = [
        "origin",
        "destination",
        "current_status",
        "carrier",
        "driver",
        "vehicle",
    ]
    list_select_related = ["carrier", "driver", "vehicle"]


@admin.register(models.ShipmentStatusEvent)
class ShipmentStatusEventAdmin(admin.ModelAdmin):
    list_display = ["shipment", "status", "event_timestamp", "source"]


@admin.register(models.Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "phone_number", "email", "carrier"]


@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["carrier", "plate_number", "device_id"]
