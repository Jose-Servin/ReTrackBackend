import uuid
from django.db import models
from django.utils import timezone


class Carrier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    mc_number = models.CharField(max_length=50, null=True, blank=True)
    account_managers = models.ManyToManyField(
        "core.User",
        related_name="managed_carriers",
        blank=True,
        help_text="ReTrack internal users managing this carrier",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CarrierContact(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        DISPATCH = "DISPATCH", "Dispatch"
        BILLING = "BILLING", "Billing"
        SAFETY = "SAFETY", "Safety"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    carrier = models.ForeignKey(
        Carrier, on_delete=models.CASCADE, related_name="vehicles"
    )
    plate_number = models.CharField(max_length=20, unique=True)
    device_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.carrier.name} - {self.plate_number}"


class ShipmentStatusEvent(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_TRANSIT = "in_transit", "In Transit"
        DELIVERED = "delivered", "Delivered"
        DELAYED = "delayed", "Delayed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.status} @ {self.event_timestamp} (Shipment {self.shipment.id})"


class Shipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    origin = models.ForeignKey(
        "locations.Location", related_name="shipments_origin", on_delete=models.PROTECT
    )
    destination = models.ForeignKey(
        "locations.Location",
        related_name="shipments_destination",
        on_delete=models.PROTECT,
    )

    scheduled_pickup = models.DateTimeField()
    scheduled_delivery = models.DateTimeField()
    actual_pickup = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)

    current_status = models.CharField(
        max_length=20,
        choices=ShipmentStatusEvent.Status.choices,
        default=ShipmentStatusEvent.Status.PENDING,
        help_text="The most recent status. Derived from status events.",
    )

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

    def __str__(self):
        return f"Shipment {self.id} ({self.current_status})"

    def update_status(self, new_status, source=None, notes=None, event_timestamp=None):
        event = ShipmentStatusEvent.objects.create(
            shipment=self,
            status=new_status,
            event_timestamp=event_timestamp or timezone.now(),
            source=source,
            notes=notes,
        )

        self.current_status = new_status

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

        self.save(
            update_fields=[
                "current_status",
                "actual_pickup",
                "actual_delivery",
                "updated_at",
            ]
        )
        return event
