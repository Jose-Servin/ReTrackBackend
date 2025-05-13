from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models
from unfold.admin import ModelAdmin


class DriverCapacityFilter(admin.SimpleListFilter):
    title = "Driver Capacity"
    parameter_name = "capacity"

    def lookups(self, request, model_admin):
        return [
            ("lte1", "Under Capacity"),
            ("btw2_3", "At Capacity"),
            ("gte4", "Over Capacity"),
        ]

    def queryset(self, request, queryset: QuerySet) -> QuerySet:
        value = self.value()
        if value == "lte1":
            return queryset.filter(available_drivers__lte=1)
        elif value == "btw2_3":
            return queryset.filter(available_drivers__gte=2, available_drivers__lte=3)
        elif value == "gte4":
            return queryset.filter(available_drivers__gte=4)
        return queryset


@admin.register(models.Carrier)
class CarrierAdmin(ModelAdmin):
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

    list_filter = [DriverCapacityFilter]
    search_fields = ["name__istartswith", "mc_number__istartswith"]

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
class CarrierContactAdmin(ModelAdmin):
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
class ShipmentAdmin(ModelAdmin):
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
    list_filter = ["carrier", "current_status"]


@admin.register(models.ShipmentStatusEvent)
class ShipmentStatusEventAdmin(ModelAdmin):
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

    list_display = [
        "first_name",
        "last_name",
        "completed_shipments",
        "phone_number",
        "email",
        "carrier",
    ]

    @admin.display(ordering="completed_shipments")
    def completed_shipments(self, driver):
        """
        Returns the number of shipments associated with the driver as a clickable link.

        The link redirects to the Shipments admin page, filtered by the selected Driver.
        """
        shipment_chagelist_url = (
            reverse("admin:shipments_shipment_changelist")
            + "?"
            + urlencode({"driver_id": str(driver.id)})
        )
        return format_html(
            f"<a href='{shipment_chagelist_url}'>{driver.completed_shipments}</a>"
        )

    def get_queryset(self, request):
        """
        Annotates the queryset with the number of shipements associated with each driver.

        Returns:
        - The annotated queryset.
        """
        return (
            super()
            .get_queryset(request)
            .annotate(completed_shipments=Count("shipment"))
        )


@admin.register(models.Vehicle)
class VehicleAdmin(ModelAdmin):
    """
    Custom admin class for the Vehicle model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    """

    list_display = ["carrier", "plate_number", "device_id"]


@admin.register(models.Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
        "weight_lb",
        "length_in",
        "width_in",
        "height_in",
        "is_fragile",
        "is_hazardous",
    ]


@admin.register(models.ShipmentItem)
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = ["shipment", "asset", "quantity", "unit_weight_lb", "notes"]
