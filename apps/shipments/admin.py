from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models


@admin.register(models.Carrier)
class CarrierAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Carrier model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    - available_drivers (callable): Custom display for the count of drivers linked to the carrier.

    Methods:
    - available_drivers(carrier): Returns the number of available drivers as a clickable link
        to the filtered driver list in the admin.
    - get_queryset(request): Annotates the queryset with the number of available drivers.
    """

    list_display = [
        "name",
        "mc_number",
        "available_drivers",
        "created_at",
        "updated_at",
    ]

    @admin.display(ordering="available_drivers")
    def available_drivers(self, carrier):
        """
        Returns the number of drivers associated with the carrier as a clickable link.

        The link redirects to the Driver admin page, filtered by the selected carrier.
        """
        drivers_changelist_url = (
            reverse("admin:shipments_driver_changelist")
            + "?"
            + urlencode({"carrier__id": str(carrier.id)})
        )
        return format_html(
            f"<a href='{drivers_changelist_url}'>{carrier.available_drivers}</a>"
        )

    def get_queryset(self, request):
        """
        Annotates the queryset with the number of drivers associated with each carrier.

        Returns:
        - The annotated queryset.
        """
        return (
            super().get_queryset(request).annotate(available_drivers=Count("drivers"))
        )


@admin.register(models.CarrierContact)
class CarrierContactAdmin(admin.ModelAdmin):
    """
    Custom admin class for the CarrierContact model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    - list_editable (list): Fields that can be edited directly from the list view.
    - list_select_related (list): Related objects to include in the query to optimize performance.
    """

    list_display = ["first_name", "last_name", "carrier", "role", "is_primary"]
    list_editable = ["is_primary"]
    list_select_related = ["carrier"]


@admin.register(models.Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Shipment model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    - list_select_related (list): Related objects to include in the query to optimize performance.
    """

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
    """
    Custom admin class for the ShipmentStatusEvent model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    """

    list_display = ["shipment", "status", "event_timestamp", "source"]


@admin.register(models.Driver)
class DriverAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Driver model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    """

    list_display = ["first_name", "last_name", "phone_number", "email", "carrier"]


@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Vehicle model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    """

    list_display = ["carrier", "plate_number", "device_id"]
