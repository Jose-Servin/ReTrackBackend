from django.db import models
from django.core.exceptions import ValidationError


class GPSDevice(models.Model):
    """
    Represents a physical GPS tracking device installed on a vehicle or asset.

    Attributes:
        serial_number (str): Unique hardware identifier for the GPS device.
        assigned_vehicle (ForeignKey): Optional link to the Vehicle currently using this device.
        is_active (bool): Whether the device is actively reporting data.
        last_seen (datetime): Timestamp of the most recent GPSTrackingPing received.
        created_at (datetime): Timestamp when the device record was created.
    """

    serial_number = models.CharField(max_length=100, unique=True)
    assigned_vehicle = models.ForeignKey(
        "shipments.Vehicle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="gps_devices",
        help_text="Vehicle currently using this GPS device.",
    )
    is_active = models.BooleanField(
        default=True, help_text="Is the device currently active?"
    )
    last_seen = models.DateTimeField(
        null=True, blank=True, help_text="Timestamp of the last received ping."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.serial_number


class GPSTrackingPing(models.Model):
    """
    Stores raw GPS telemetry data from a GPS device.

    Attributes:
        gps_device (ForeignKey): The device that reported this ping.
        latitude (decimal): Latitude coordinate.
        longitude (decimal): Longitude coordinate.
        recorded_at (datetime): Timestamp when the GPS reading was taken.
        speed_mph (float): Optional. Speed of the device at time of ping (in miles per hour).
        heading (float): Optional. Direction the device is facing (in degrees).
        created_at (datetime): Record creation time.

    Constraints:
        - A GPS device cannot have two pings with the same recorded_at timestamp.
    """

    gps_device = models.ForeignKey(
        "GPSDevice",
        on_delete=models.CASCADE,
        related_name="pings",
        help_text="The GPS device that generated this ping.",
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, help_text="Latitude at time of ping."
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, help_text="Longitude at time of ping."
    )
    recorded_at = models.DateTimeField(help_text="Timestamp of the GPS reading.")
    speed_mph = models.FloatField(
        null=True, blank=True, help_text="Optional. Speed at time of ping."
    )
    heading = models.FloatField(
        null=True, blank=True, help_text="Optional. Direction of movement in degrees."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["gps_device", "recorded_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["gps_device", "recorded_at"],
                name="unique_ping_per_device_timestamp",
            )
        ]

    def __str__(self) -> str:
        return f"{self.gps_device.serial_number} @ {self.recorded_at:%m/%d %H:%M}"


class GPSTrackingEvent(models.Model):
    """
    Captures meaningful movement or location-based events derived from GPS pings.

    Attributes:
        gps_device (ForeignKey): The GPS device associated with this event.
        vehicle (ForeignKey): Optional. Vehicle involved in the event.
        shipment (ForeignKey): Optional. Shipment related to the event.
        event_type (str): Type of event (e.g., arrived, departed, stopped).
        event_timestamp (datetime): When the event occurred.
        location (ForeignKey): Optional. Known location related to the event (e.g., warehouse geofence).
        note (str): Optional. Additional context or system explanation.
        created_at (datetime): When the event record was created.

    Constraints:
        - A GPS device cannot have multiple events of the same type at the same timestamp.
        (unique on [gps_device, event_type, event_timestamp])

    Validation:
        - Ensures tracking events are recorded in chronological order per device.
        (i.e., no event may occur earlier than the latest known event for that GPS device)
    """

    class EventType(models.TextChoices):
        ARRIVED = "arrived", "Arrived"
        DEPARTED = "departed", "Departed"
        STOPPED = "stopped", "Stopped"
        IN_TRANSIT = "in_transit", "In Transit"
        CUSTOM = "custom", "Custom"

    gps_device = models.ForeignKey(
        "GPSDevice",
        on_delete=models.CASCADE,
        related_name="tracking_events",
        help_text="Device responsible for this tracking event.",
    )
    vehicle = models.ForeignKey(
        "shipments.Vehicle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Vehicle involved at the time of the event.",
    )
    shipment = models.ForeignKey(
        "shipments.Shipment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Optional shipment related to the tracking event.",
    )
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        help_text="Classified type of tracking event.",
    )
    event_timestamp = models.DateTimeField(help_text="When the event occurred.")
    location = models.ForeignKey(
        "locations.Location",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Optional known location or geofence involved.",
    )
    note = models.TextField(blank=True, help_text="Optional context or explanation.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event_timestamp"]
        constraints = [
            models.UniqueConstraint(
                fields=["gps_device", "event_type", "event_timestamp"],
                name="unique_tracking_event_per_timestamp",
            )
        ]

    def __str__(self) -> str:
        return f"{self.event_type} @ {self.event_timestamp:%m/%d %H:%M} | {self.gps_device.serial_number}"

    def clean(self) -> None:
        # Chronological validation
        # TODO: Document clean method understanding
        latest_event = (
            GPSTrackingEvent.objects.filter(gps_device=self.gps_device)
            .exclude(pk=self.pk)
            .order_by("-event_timestamp")
            .first()
        )
        if latest_event and latest_event.event_timestamp > self.event_timestamp:
            raise ValidationError(
                "Tracking events must be chronological for each device."
            )
