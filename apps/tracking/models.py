from django.db import models


class GPSDevice(models.Model):
    """
    Represents a physical GPS tracking device installed on a vehicle or asset.

    Attributes:
        device_id (str): Unique hardware identifier for the GPS device.
        assigned_vehicle (ForeignKey): Optional link to the Vehicle currently using this device.
        is_active (bool): Whether the device is actively reporting data.
        last_seen (datetime): Timestamp of the most recent GPSTrackingPing received.
        created_at (datetime): Timestamp when the device record was created.
    """

    device_id = models.CharField(max_length=100, unique=True)
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


class GPSTrackingPing(models.Model):
    """
    Stores raw GPS telemetry data from a GPS device.

    Attributes:
        gps_device (ForeignKey): The device that reported this ping.
        latitude (decimal): Latitude coordinate.
        longitude (decimal): Longitude coordinate.
        timestamp (datetime): Timestamp when the GPS reading was taken.
        speed_mph (float): Optional. Speed of the device at time of ping (in miles per hour).
        heading (float): Optional. Direction the device is facing (in degrees).
        created_at (datetime): Record creation time.
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
    timestamp = models.DateTimeField(help_text="Timestamp of the GPS reading.")
    speed_mph = models.FloatField(
        null=True, blank=True, help_text="Optional. Speed at time of ping."
    )
    heading = models.FloatField(
        null=True, blank=True, help_text="Optional. Direction of movement in degrees."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["gps_device", "timestamp"]),
        ]


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
