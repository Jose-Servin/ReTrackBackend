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
    """
    Custom filter for the Carrier admin that segments carriers
    based on the number of drivers assigned to them.

    Options:
        - Under Capacity (≤ 1)
        - At Capacity (2-3)
        - Over Capacity (≥ 4)

    This filter annotates each Carrier with a 'driver_count' using
    an aggregate Count of related Driver records.
    """

    title = "Driver Capacity"
    parameter_name = "capacity"

    def lookups(self, request, model_admin) -> list[tuple[str, str]]:
        return [
            ("lte1", "Under Capacity (≤ 1)"),
            ("btw2_3", "At Capacity (2-3)"),
            ("gte4", "Over Capacity (≥ 4)"),
        ]

    def queryset(self, request, queryset: QuerySet) -> QuerySet:
        # Add driver count annotation for filtering
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
    Custom admin configuration for the Carrier model.

    Enhancements:
        - Displays the number of available drivers via a clickable link.
        - Annotates each Carrier with a precomputed driver count to avoid N+1 queries.
        - Applies prefetching on 'drivers' to reduce query count for related lookups.

    Attributes:
        list_display: Fields and computed values to show in the list view.
        list_filter: Custom filters, including DriverCapacityFilter for segmentation.
        search_fields: Enables partial matching on Carrier name and MC number.

    Methods:
        get_queryset(request):
            Annotates the queryset with 'driver_count' (Count of related Drivers)
            and prefetches the reverse FK to avoid extra queries.

        available_drivers(carrier):
            Displays the number of related Drivers as a clickable link to
            the Driver changelist filtered by the Carrier.

        get_readonly_fields(request, obj):
            Prevents editing of 'mc_number' after initial creation.
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

    def get_queryset(self, request):
        # Efficiently fetch driver count and prefetch drivers to avoid N+1 issues
        qs = super().get_queryset(request)
        return qs.annotate(driver_count=Count("drivers")).prefetch_related("drivers")

    @admin.display(ordering="driver_count")
    def available_drivers(self, carrier) -> SafeText:
        """
        Returns the number of drivers associated with the carrier
        as a clickable link to the filtered Driver changelist.
        """
        drivers_changelist_url = (
            reverse("admin:shipments_driver_changelist")
            + "?"
            + urlencode({"carrier__id": str(carrier.id)})
        )
        return format_html(
            f"<a href='{drivers_changelist_url}'>{carrier.driver_count}</a>"
        )

    def get_readonly_fields(self, request, obj=None):
        # Make mc_number read-only on updates to preserve its integrity
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
    """
    Custom filter for Shipment list view that filters shipments by their
    most recent status event.

    Implements a subquery to annotate each Shipment with its latest status,
    then applies a filter based on the selected value.

    Options are derived from the ShipmentStatusEvent.Status choices.
    """

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
    """
    Inline configuration for displaying ShipmentItems within a Shipment form.

    Optimizations:
    - Uses select_related on the 'asset' foreign key to avoid N+1 queries
        when rendering asset fields in the inline form.
    """

    model = models.ShipmentItem
    autocomplete_fields = ["asset"]
    extra = 0
    min_num = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("asset")  # Prevents per-row asset lookups


@admin.register(models.Shipment)
class ShipmentAdmin(ModelAdmin):
    """
    Custom admin class for the Shipment model.

    Optimizations:
    - Annotates each Shipment with its latest status to avoid N+1 queries
        caused by the `current_status` property.
    - Uses select_related for all forward foreign keys displayed in the list view,
        including chained lookups needed by __str__ methods (e.g., vehicle__carrier, driver__carrier).
    - Includes inline editing for associated ShipmentItems with optimized asset lookup.

    Attributes:
    - autocomplete_fields: Reduces load on dropdowns for high-volume FK fields.
    - inlines: Shows ShipmentItems inline within the Shipment form.
    - list_display: Displays key relationships and annotated current status.
    - list_select_related: Ensures efficient FK resolution in the list view.
    - list_filter: Enables filtering by carrier and annotated current status.
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
    list_select_related = ["carrier", "driver", "vehicle", "origin", "destination"]
    list_filter = ["carrier", CurrentStatusFilter]

    def get_queryset(self, request):
        # Base queryset with select_related for all necessary forward FKs
        qs = (
            super()
            .get_queryset(request)
            .select_related(
                "carrier",
                "driver",
                "driver__carrier",  # Required due to Driver.__str__()
                "vehicle",
                "vehicle__carrier",  # Required due to Vehicle.__str__()
                "origin",
                "destination",
            )
        )

        # Annotate the latest status using a subquery for efficient filtering and display
        latest_status_subquery = models.ShipmentStatusEvent.objects.filter(
            shipment=OuterRef("pk")
        ).order_by("-event_timestamp")

        return qs.annotate(
            latest_status=Subquery(latest_status_subquery.values("status")[:1])
        )

    @admin.display(ordering="latest_status")
    def current_status(self, obj) -> str:
        """
        Displays the most recent status for the shipment, derived from
        the latest related ShipmentStatusEvent. Falls back to a dash if unavailable.
        """
        return obj.latest_status or "—"


@admin.register(models.ShipmentStatusEvent)
class ShipmentStatusEventAdmin(ModelAdmin):
    """
    Custom admin class for the ShipmentStatusEvent model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    """

    list_display = ["id", "shipment", "status", "event_timestamp", "source", "notes"]


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
    list_select_related = ["carrier"]

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
            .select_related("carrier")
        )

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


@admin.register(models.Vehicle)
class VehicleAdmin(ModelAdmin):
    """
    Custom admin class for the Vehicle model.

    Attributes:
    - list_display (list): Fields to display in the list view.
    """

    list_display = ["carrier", "plate_number", "created_at", "updated_at"]
    search_fields = ["carrier__name__istartswith", "plate_number__istartswith"]
    list_select_related = ["carrier"]


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

    def get_queryset(self, request):
        qs = (
            super()
            .get_queryset(request)
            .select_related(
                "asset",
                "shipment__origin",
                "shipment__destination",
            )
        )
        return qs
