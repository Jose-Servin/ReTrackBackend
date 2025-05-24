from typing import Any, Sequence
from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode
from django.utils.safestring import SafeText
from . import models
from unfold.admin import ModelAdmin
from django.db.models import OuterRef, Subquery


class DriverCapacityFilter(admin.SimpleListFilter):
    title = "Driver Capacity"
    parameter_name = "capacity"

    def lookups(self, request, model_admin) -> list[tuple[str, str]]:
        return [
            ("lte1", "Under Capacity (≤ 1)"),
            ("btw2_3", "At Capacity (2-3)"),
            ("gte4", "Over Capacity (≥ 4)"),
        ]

    def queryset(self, request, queryset: QuerySet) -> QuerySet:
        annotated = queryset.annotate(driver_count=Count("drivers"))
        value = self.value()
        if value == "lte1":
            return annotated.filter(driver_count__lte=1)
        elif value == "btw2_3":
            return annotated.filter(driver_count__gte=2, driver_count__lte=3)
        elif value == "gte4":
            return annotated.filter(driver_count__gte=4)
        return annotated


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
    def available_drivers(self, carrier) -> SafeText:
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

    def get_readonly_fields(
        self, request, obj=None
    ):  # -> list[str] | list[Any]:  # -> list[str] | list[Any]:# -> list[str] | list[Any]:
        # obj is None when creating a new object
        if obj:  # Editing an existing Carrier
            return ["mc_number"]
        return []  # Allow editing mc_number when creating


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


class CurrentStatusFilter(admin.SimpleListFilter):
    title = "Current Status"
    parameter_name = "current_status"

    def lookups(
        self, request, model_admin
    ) -> Sequence[tuple[models.ShipmentStatusEvent.Status, str]]:
        return models.ShipmentStatusEvent.Status.choices

    def queryset(self, request, queryset) -> QuerySet[Any]:
        if self.value():
            # Subquery to get latest status per shipment
            latest_status_subquery = models.ShipmentStatusEvent.objects.filter(
                shipment=OuterRef("pk")
            ).order_by("-event_timestamp")

            # Annotate each shipment with the latest status
            queryset = queryset.annotate(
                latest_status=Subquery(latest_status_subquery.values("status")[:1])
            )

            return queryset.filter(latest_status=self.value())

        return queryset


class ShipmentItemsInline(admin.TabularInline):
    model = models.ShipmentItem
    autocomplete_fields = ["asset"]
    extra = 0
    min_num = 1


@admin.register(models.Shipment)
class ShipmentAdmin(ModelAdmin):
    """
    Custom admin class for the Shipment model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    - list_select_related (list): Related objects to include in the query to optimize performance.
    """

    autocomplete_fields = ["carrier", "driver", "vehicle"]
    inlines = [ShipmentItemsInline]
    list_display = [
        "origin",
        "destination",
        "current_status",
        "carrier",
        "driver",
        "vehicle",
    ]
    list_select_related = ["carrier", "driver", "vehicle"]
    list_filter = ["carrier", CurrentStatusFilter]


@admin.register(models.ShipmentStatusEvent)
class ShipmentStatusEventAdmin(ModelAdmin):
    """
    Custom admin class for the ShipmentStatusEvent model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    """

    list_display = ["shipment", "status", "event_timestamp", "source"]


@admin.register(models.Driver)
class DriverAdmin(ModelAdmin):
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

    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    @admin.display(ordering="completed_shipments")
    def completed_shipments(self, driver) -> SafeText:
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

    def get_queryset(self, request) -> QuerySet:
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

    list_display = ["carrier", "plate_number"]
    search_fields = ["carrier__name__istartswith", "plate_number__istartswith"]


@admin.register(models.Asset)
class AssetAdmin(ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
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
    search_fields = ["name__istartswith"]


@admin.register(models.ShipmentItem)
class ShipmentItemAdmin(ModelAdmin):
    list_display = ["asset", "shipment", "quantity", "unit_weight_lb", "notes"]
