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
    slug = models.SlugField()

    def __str__(self):
        return f"{self.origin} → {self.destination} [{self.current_status}]"

    def update_status(self, new_status, source=None, event_timestamp=None):
        event = ShipmentStatusEvent.objects.create(
            shipment=self,
            status=new_status,
            event_timestamp=event_timestamp or timezone.now(),
            source=source,
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
