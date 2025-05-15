import uuid
from django.db import models
from django.utils import timezone


class Carrier(models.Model):
    name = models.CharField(max_length=255)
    mc_number = models.CharField(max_length=50)
    # TODO: replace with FK to core.User when model is defined
    # account_managers
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class CarrierContact(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        DISPATCH = "DISPATCH", "Dispatch"
        BILLING = "BILLING", "Billing"
        SAFETY = "SAFETY", "Safety"

    carrier = models.ForeignKey(
        "Carrier", on_delete=models.CASCADE, related_name="contacts"
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.OWNER,
        blank=True,
    )
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["carrier"],
                condition=models.Q(is_primary=True),
                name="unique_primary_contact_per_carrier",
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Driver(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    carrier = models.ForeignKey(
        Carrier, on_delete=models.CASCADE, related_name="drivers"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Vehicle(models.Model):
    carrier = models.ForeignKey(
        Carrier, on_delete=models.CASCADE, related_name="vehicles"
    )
    plate_number = models.CharField(max_length=20, unique=True)
    device_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.carrier.name} - {self.plate_number}"


class Asset(models.Model):
    """
    Represents a physical item or good that can be shipped.

    Attributes:
        name (str): The name or identifier of the asset.
        slug (SlugField): A URL-friendly label used to reference the asset.
        description (str): Optional detailed information about the asset.
        weight_lb (Decimal): The weight of a single unit in pounds.
        length_in (Decimal): The length of the asset in inches.
        width_in (Decimal): The width of the asset in inches.
        height_in (Decimal): The height of the asset in inches.
        is_fragile (bool): Indicates whether the asset requires special handling due to fragility.
        is_hazardous (bool): Indicates whether the asset is considered hazardous material.
        created_at (DateTime): Timestamp when the asset was first created.
        updated_at (DateTime): Timestamp of the most recent update to the asset.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField()
    weight_lb = models.DecimalField(
        max_digits=7, decimal_places=2, help_text="Weight of a single unit in pounds"
    )
    length_in = models.DecimalField(
        max_digits=7, decimal_places=2, help_text="Length of the item in inches"
    )
    width_in = models.DecimalField(
        max_digits=7, decimal_places=2, help_text="Width of the item in inches"
    )
    height_in = models.DecimalField(
        max_digits=7, decimal_places=2, help_text="Height of the item in inches"
    )
    is_fragile = models.BooleanField(default=False)
    is_hazardous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ShipmentStatusEvent(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_TRANSIT = "in_transit", "In Transit"
        DELIVERED = "delivered", "Delivered"
        DELAYED = "delayed", "Delayed"
        CANCELLED = "cancelled", "Cancelled"

    shipment = models.ForeignKey(
        "Shipment", on_delete=models.PROTECT, related_name="status_events"
    )
    status = models.CharField(max_length=20, choices=Status.choices)
    event_timestamp = models.DateTimeField(default=timezone.now)
    source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="System or user that triggered this status change",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.status} @ {self.event_timestamp} (Shipment {self.shipment.id})"


class Shipment(models.Model):
    # TODO: replace with FK to Location when model is defined
    origin = models.CharField(max_length=255)
    # TODO: replace with FK to Location when model is defined
    destination = models.CharField(max_length=255)
    scheduled_pickup = models.DateTimeField()
    scheduled_delivery = models.DateTimeField()
    actual_pickup = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)

    carrier = models.ForeignKey(
        "Carrier", on_delete=models.SET_NULL, null=True, blank=True
    )
    driver = models.ForeignKey(
        "Driver", on_delete=models.SET_NULL, null=True, blank=True
    )
    vehicle = models.ForeignKey(
        "Vehicle", on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def current_status(self):
        latest_event = self.status_events.order_by("-event_timestamp").first()
        return (
            latest_event.status if latest_event else ShipmentStatusEvent.Status.PENDING
        )

    def __str__(self):
        return f"{self.origin} → {self.destination} [{self.current_status}]"

    def update_status(self, new_status, source=None, event_timestamp=None):
        event = ShipmentStatusEvent.objects.create(
            shipment=self,
            status=new_status,
            event_timestamp=event_timestamp or timezone.now(),
            source=source,
        )

        # TODO: align data from ShipmentStatusEvent and Shipment tables to follow these constraints
        # actual_pickup from Shipement model should be the same value as event_timestamp for status IN_TRANSIT
        # actual_delivery from Shipement model should be the same value as event_timestamp for status DELIVERED

        if (
            new_status == ShipmentStatusEvent.Status.IN_TRANSIT
            and not self.actual_pickup
        ):
            self.actual_pickup = event.event_timestamp

        if (
            new_status == ShipmentStatusEvent.Status.DELIVERED
            and not self.actual_delivery
        ):
            self.actual_delivery = event.event_timestamp

        self.save(update_fields=["actual_pickup", "actual_delivery", "updated_at"])
        return event


class ShipmentItem(models.Model):
    """
    Represents a specific asset included in a shipment.

    Attributes:
        shipment (ForeignKey): A reference to the Shipment that this item is part of.
            - Deleting the shipment will also delete all associated shipment items.
        asset (ForeignKey): The asset being shipped.
            - Protected to prevent deletion of the asset if referenced in any shipment.
        quantity (int): The number of units of the asset included in the shipment.
        unit_weight_lb (Decimal): The recorded weight per unit at the time of shipment, in pounds.
            - This value is snapshotted from the Asset model to preserve historical accuracy.
        notes (str): Optional notes or comments related to this shipment item (e.g., "damaged packaging").

    Methods:
        total_weight(): Returns the total weight of this item in the shipment (quantity * unit weight).
    """

    shipment = models.ForeignKey(
        "Shipment", on_delete=models.CASCADE, related_name="items"
    )
    asset = models.ForeignKey(
        "Asset", on_delete=models.PROTECT, related_name="shipment_items"
    )
    quantity = models.PositiveIntegerField()

    unit_weight_lb = models.DecimalField(
        max_digits=7, decimal_places=2, help_text="Weight per unit in pounds"
    )

    notes = models.TextField(blank=True, null=True)

    def total_weight(self):
        return self.quantity * self.unit_weight_lb

    def __str__(self):
        return f"{self.quantity} * {self.asset.name} (Shipment ID: {self.shipment_id})"
