import uuid
from decimal import Decimal
from typing import Literal
from autoslug import AutoSlugField
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.db.models import Q, CheckConstraint
from django.db.models.functions import Upper
from .validators import (
    plate_validator,
    phone_validator,
    sku_validator,
    mc_number_validator,
)


class Carrier(models.Model):
    """
    Represents a freight carrier in ReTrackLogistics.

    Designed to support both operational workflows and future data engineering use cases,
    including ingestion traceability, warehouse modeling, and reconciliation.

    Fields:
        name (str): Human-readable carrier name.
        mc_number (str): Unique Motor Carrier number (case-insensitive, trimmed).
        external_id (str): Optional ID from external systems (e.g., CRM, ERP).
        status (str): Operational state — Active, Suspended, or Terminated.
        mc_verified (bool): Flag indicating MC number was externally validated.
        created_by_system (str): Source system or method that created the record.
        created_at / updated_at (datetime): Timestamps for record lifecycle.

    Properties:
        available_drivers (int): Count of assigned drivers.
        capacity_status (str): Driver count label — Under, At, or Over Capacity.

    Methods:
        clean(): Enforces uniqueness of normalized `mc_number`.
        save(): Normalizes fields and triggers validation.

    Note:
        This model is raw-layer aware and can be extended with ingestion audit logs.
    """

    CREATED_BY_SYSTEM_PREFIXES = {
        "CRM System": "CRM_",
        "Manual Entry": "M_",
        "Partner API": "API_",
        "Legacy Migration": "LM_",
    }

    name = models.CharField(max_length=255)
    mc_number = models.CharField(
        max_length=50,
        validators=[mc_number_validator],
        db_index=True,
    )
    external_id = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        help_text="System-generated UUID with a source-specific prefix (e.g., CRM_, API_, etc.)",
    )

    class CarrierStatus(models.TextChoices):
        ACTIVE = "Active", "Active"
        SUSPENDED = "Suspended", "Suspended"
        TERMINATED = "Terminated", "Terminated"

    status = models.CharField(
        max_length=50,
        choices=CarrierStatus.choices,
        default=CarrierStatus.ACTIVE,
    )
    mc_verified = models.BooleanField(default=False)
    created_by_system = models.CharField(
        max_length=100,
        choices=[(key, key) for key in CREATED_BY_SYSTEM_PREFIXES.keys()],
        help_text="Source system or method that created this record",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation first (calls `clean()`)

        if self.mc_number:
            self.mc_number = self.mc_number.upper().strip()

        if not self.external_id:
            # At this point, created_by_system is already validated in clean()
            prefix = self.__class__.CREATED_BY_SYSTEM_PREFIXES[self.created_by_system]
            self.external_id = f"{prefix}{uuid.uuid4().hex}"

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if (
            not self.created_by_system
            or self.created_by_system not in self.__class__.CREATED_BY_SYSTEM_PREFIXES
        ):
            raise ValidationError(
                {
                    "created_by_system": "Must be one of: CRM System, Manual Entry, Partner API, or Legacy Migration"
                }
            )

        if self.mc_number:
            # Normalize to match how the uniqueness constraint is enforced
            normalized_mc_number = self.mc_number.upper().strip()

            # Exclude self to avoid false positives during updates
            existing = Carrier.objects.annotate(
                normalized_mc_number=Upper("mc_number")
            ).filter(normalized_mc_number=normalized_mc_number)

            if self.pk:
                existing = existing.exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError({"mc_number": "This MC number already exists."})

    @property
    def available_drivers(self) -> int:
        """
        Returns the number of drivers linked to this carrier.
        """
        return self.drivers.count()

    @property
    def capacity_status(
        self,
    ) -> Literal["Under Capacity"] | Literal["At Capacity"] | Literal["Over Capacity"]:
        """
        Returns a string classifying the driver count as:
        - Under Capacity (≤ 1)
        - At Capacity (2 - 3)
        - Over Capacity (≥ 4)
        """
        count = self.available_drivers
        if count <= 1:
            return "Under Capacity"
        elif 2 <= count <= 3:
            return "At Capacity"
        return "Over Capacity"


class CarrierContact(models.Model):
    """
    Represents a point of contact for a specific carrier.

    Attributes:
        carrier (Carrier): The carrier this contact is associated with.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Unique email address for the contact. Enforced as lowercase.
        phone_number (str or None): Optional US-formatted phone number (e.g., "832-123-4567").
        role (str): The contact's role within the carrier organization. One of: "Owner", "Dispatch", "Billing", "Safety".
        is_primary (bool): Indicates if this contact is the primary point of contact for the carrier.
        created_at (datetime.datetime): Timestamp when the contact was created.
        updated_at (datetime.datetime): Timestamp when the contact was last updated.

    Constraints:
        - Only one primary contact (`is_primary=True`) is allowed per carrier.
        - This is enforced at both the database level (via UniqueConstraint) and the application level (via `clean()`).

    Methods:
        clean():
            Validates that no other primary contact exists for the same carrier.

        save(*args, **kwargs):
            Normalizes the phone number (removes dashes) and email (lowercased), then saves the instance.
    """

    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        DISPATCH = "DISPATCH", "Dispatch"
        BILLING = "BILLING", "Billing"
        SAFETY = "SAFETY", "Safety"

    carrier = models.ForeignKey(
        "Carrier", on_delete=models.PROTECT, related_name="contacts"
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=12,
        validators=[phone_validator],
        blank=True,
        null=True,
        help_text="Format: 832-123-4567 or 8321234567",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.DISPATCH)
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

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def clean(self) -> None:
        # Ensure no more than one primary contact per carrier at the form level
        if self.is_primary:
            existing = CarrierContact.objects.filter(
                carrier=self.carrier, is_primary=True
            )
            if self.pk:
                existing = existing.exclude(pk=self.pk)  # skip self during edit
            if existing.exists():
                raise ValidationError("This carrier already has a primary contact.")

    def save(self, *args, **kwargs) -> None:
        # Normalize phone number (strip dashes)
        if self.phone_number:
            self.phone_number = self.phone_number.replace("-", "")
        # Normalize email to lowercase to enforce case-insensitive uniqueness
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)


class Driver(models.Model):
    """
    Represents a driver employed by a carrier.

    Attributes:
        first_name (str): First name of the driver.
        last_name (str): Last name of the driver.
        phone_number (str or None): Optional US-formatted phone number (e.g., "832-123-4567").
        email (str): Unique email address for the driver. Stored in lowercase for case-insensitive uniqueness.
        carrier (Carrier): The carrier this driver is associated with.
        created_at (datetime.datetime): Timestamp when the driver record was created.
        updated_at (datetime.datetime): Timestamp of the last update to the driver record.

    Methods:
        save(*args, **kwargs):
            Normalizes the phone number (removes dashes) and email (lowercased), then saves the instance.
    """

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=12,
        validators=[phone_validator],
        blank=True,
        null=True,
        help_text="Format: 832-123-4567 or 8321234567",
    )
    email = models.EmailField(unique=True)
    carrier = models.ForeignKey(
        Carrier, on_delete=models.PROTECT, related_name="drivers"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs) -> None:
        # Normalize phone number (strip dashes)
        if self.phone_number:
            self.phone_number = self.phone_number.replace("-", "")
        # Normalize email to lowercase to enforce case-insensitive uniqueness
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)


class Vehicle(models.Model):
    """
    Represents a vehicle owned or operated by a carrier.

    Attributes:
        carrier (Carrier): The carrier that owns or operates this vehicle.
        plate_number (str): Unique license plate identifier for the vehicle.
            Must consist of letters, numbers, or hyphens (no spaces or special characters).
            Input is case-insensitive; automatically normalized to uppercase on save.
        created_at (datetime.datetime): Timestamp when the vehicle record was created.
        updated_at (datetime.datetime): Timestamp of the last update to the vehicle record.

    Methods:
        save(*args, **kwargs):
            Normalizes the `plate_number` to uppercase and saves the instance.
    """

    carrier = models.ForeignKey(
        Carrier, on_delete=models.PROTECT, related_name="vehicles"
    )
    plate_number = models.CharField(
        max_length=20, unique=True, validators=[plate_validator]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.plate_number

    def save(self, *args, **kwargs) -> None:
        # Normalize plate_number to uppercase to enforce case-insensitive uniqueness
        if self.plate_number:
            self.plate_number = self.plate_number.upper()
        super().save(*args, **kwargs)


class Asset(models.Model):
    """
    Represents a physical item or product that can be shipped.

    Attributes:
        name (str): The name or human-readable identifier of the asset.
        sku (str): A unique, case-insensitive stock-keeping unit. Normalized to uppercase on save.
        description (str): Optional detailed description of the asset.
        slug (str): A unique, URL-friendly identifier auto-generated from `name` on create.
        weight_lb (Decimal): Weight of a single unit in pounds. Must be greater than 0.
        length_in (Decimal): Length of the item in inches. Must be greater than 0.
        width_in (Decimal): Width of the item in inches. Must be greater than 0.
        height_in (Decimal): Height of the item in inches. Must be greater than 0.
        is_fragile (bool): Indicates whether the item is fragile and needs special handling.
        is_hazardous (bool): Indicates whether the item contains hazardous material.
        created_at (datetime.datetime): Timestamp when the asset was created.
        updated_at (datetime.datetime): Timestamp of the most recent update to the asset.

    Properties:
        volume_cubic_in (Decimal): Computed volume in cubic inches (L × W × H).
        needs_special_handling (bool): Returns `True` if the item is both fragile and hazardous.

    Methods:
        clean():
            Validates that the SKU is unique (case-insensitive) across all assets.

        save(*args, **kwargs):
            Normalizes the SKU to uppercase, runs full validation, and saves the asset.
    """

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=64, validators=[sku_validator])
    description = models.TextField(blank=True)
    slug = AutoSlugField(
        populate_from="name",
        unique=True,
        always_update=False,  # set once on create
        blank=True,  # allows omitting in forms/serializers
    )
    weight_lb = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Weight of a single unit in pounds",
    )
    length_in = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Length of the item in inches",
    )
    width_in = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Width of the item in inches",
    )
    height_in = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Height of the item in inches",
    )
    is_fragile = models.BooleanField(default=False)
    is_hazardous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(Upper("sku"), name="unique_upper_sku")]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()  # Triggers `clean()` before saving
        if self.sku:
            self.sku = self.sku.upper().strip()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.sku:
            # Normalize to match how the uniqueness constraint is enforced
            normalized_sku = self.sku.upper().strip()

            # Exclude self to avoid false positives during updates
            existing = Asset.objects.annotate(normalized_sku=Upper("sku")).filter(
                normalized_sku=normalized_sku
            )

            if self.pk:
                existing = existing.exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError({"sku": "This SKU already exists."})

    @property
    def volume_cubic_in(self) -> Decimal:
        return self.length_in * self.width_in * self.height_in

    @property
    def needs_special_handling(self) -> bool:
        """
        Returns True if the asset is both fragile and hazardous,
        signaling that it may require additional compliance or safety measures.
        """
        return self.is_fragile and self.is_hazardous


class ShipmentStatusEvent(models.Model):
    """
    Represents a lifecycle event in the status history of a shipment.

    Attributes:
        shipment (Shipment): The shipment associated with this status event.
        status (str): The shipment status at the time of the event. One of:
            "Pending", "In Transit", "Delivered", "Delayed", or "Cancelled".
        event_timestamp (datetime.datetime): The time the event occurred. Can be historical or real-time.
        source (str or None): Optional system or user that triggered the event.
        notes (str or None): Optional notes providing context for the event.
        created_at (datetime.datetime): Timestamp when the event record was created.
        updated_at (datetime.datetime): Timestamp of the most recent update to the event record.

    Constraints:
        - Each (shipment, status, event_timestamp) tuple must be unique.
        - Events are ordered chronologically by `event_timestamp`.

    Methods:
        clean():
            Validates:
            - The event timestamp must not precede the latest existing event for the shipment.
            - No duplicate status events (same shipment, status, and timestamp).

        __str__():
            Returns a human-readable label like "In Transit @ 06/24 13:45 (Shipment #42)".

    Notes:
        This model is the single source of truth for a shipment's status history.
        Validation occurs at both the application level (`clean()`) and database level
        (`UniqueConstraint`) to ensure chronological integrity and prevent duplicates.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_TRANSIT = "in_transit", "In Transit"
        DELIVERED = "delivered", "Delivered"
        DELAYED = "delayed", "Delayed"
        CANCELLED = "cancelled", "Cancelled"

    shipment = models.ForeignKey(
        "Shipment", on_delete=models.CASCADE, related_name="status_events"
    )
    status = models.CharField(max_length=20, choices=Status.choices)
    event_timestamp = models.DateTimeField(default=timezone.now)
    source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="System or user that triggered this status change",
    )
    notes = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Optional notes about this status event.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shipment", "status", "event_timestamp"],
                name="unique_status_event_per_timestamp",
            )
        ]
        ordering = ["event_timestamp"]

    def __str__(self) -> str:
        ts = self.event_timestamp.strftime("%m/%d %H:%M")
        return f"{self.get_status_display()} @ {ts} (Shipment #{self.shipment_id})"

    def clean(self) -> None:
        # Chronological validation
        latest_event = (
            ShipmentStatusEvent.objects.filter(shipment=self.shipment)
            .exclude(pk=self.pk)
            .order_by("-event_timestamp")
            .first()
        )
        if latest_event and latest_event.event_timestamp > self.event_timestamp:
            raise ValidationError(
                "Cannot record an event earlier than the latest known status event."
            )

        # Duplicate check (customizes DB constraint error)
        duplicate = (
            ShipmentStatusEvent.objects.exclude(pk=self.pk)
            .filter(
                shipment=self.shipment,
                status=self.status,
                event_timestamp=self.event_timestamp,
            )
            .exists()
        )

        if duplicate:
            raise ValidationError(
                "This exact status event already exists — duplicate entries are not allowed."
            )


class Shipment(models.Model):
    """
    Represents a shipment of goods from an origin to a destination.

    Attributes:
        origin (Location): The origin location of the shipment.
        destination (Location): The destination location of the shipment.
        scheduled_pickup (datetime.datetime): Planned pickup datetime.
        scheduled_delivery (datetime.datetime): Planned delivery datetime.
        actual_pickup (datetime.datetime or None): Actual pickup time, typically inferred from status events.
        actual_delivery (datetime.datetime or None): Actual delivery time, typically inferred from status events.
        carrier (Carrier or None): The carrier assigned to fulfill the shipment.
        driver (Driver or None): The driver assigned to handle the shipment.
        vehicle (Vehicle or None): The vehicle assigned to transport the shipment.
        created_at (datetime.datetime): Timestamp when the shipment record was created.
        updated_at (datetime.datetime): Timestamp of the most recent update to the shipment.

    Properties:
        current_status (str): The most recent status of the shipment, derived from related status events.
            Defaults to "Pending" if no events exist.

    Methods:
        clean():
            Validates business rules:
            - Scheduled delivery must occur after scheduled pickup.
            - Actual delivery must occur after actual pickup.
            - Assigned driver and vehicle must belong to the assigned carrier.
            - Origin and destination must be different.

        record_status_event(new_status, source=None, event_timestamp=None) -> ShipmentStatusEvent:
            Creates a new status event for the shipment and updates actual pickup/delivery timestamps
            if applicable (e.g., sets actual_pickup on first In Transit event).

    Meta:
        ordering: Shipments are ordered by scheduled pickup time (ascending).
    """

    scheduled_pickup = models.DateTimeField()
    scheduled_delivery = models.DateTimeField()
    actual_pickup = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)

    origin = models.ForeignKey(
        "locations.Location",
        on_delete=models.PROTECT,
        null=False,
        related_name="shipments_origin",
    )

    destination = models.ForeignKey(
        "locations.Location",
        on_delete=models.PROTECT,
        null=False,
        related_name="shipments_destination",
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

    class Meta:
        ordering = ["scheduled_pickup"]

    @property
    def current_status(
        self,
    ):
        latest_event = self.status_events.order_by("-event_timestamp").first()
        return (
            latest_event.status if latest_event else ShipmentStatusEvent.Status.PENDING
        )

    def __str__(self) -> str:
        return f"{self.origin} → {self.destination}"

    def clean(self) -> None:
        """
        Validates scheduling and assignment consistency at the model level.

        Raises:
            ValidationError: If any of the business rules are violated.
        """

        errors = {}

        # 1. Validate scheduled dates
        if self.scheduled_pickup and self.scheduled_delivery:
            if self.scheduled_delivery < self.scheduled_pickup:
                errors["scheduled_delivery"] = (
                    "Scheduled delivery cannot be before scheduled pickup."
                )

        # 2. Validate actual dates
        if self.actual_pickup and self.actual_delivery:
            if self.actual_delivery < self.actual_pickup:
                errors["actual_delivery"] = (
                    "Actual delivery cannot be before actual pickup."
                )

        # 3. Ensure driver belongs to carrier (if both are assigned)
        if self.carrier and self.driver:
            if self.driver.carrier_id != self.carrier_id:
                errors["driver"] = (
                    "Selected driver does not belong to the assigned carrier."
                )

        # 4. Ensure vehicle belongs to carrier (if both are assigned)
        if self.carrier and self.vehicle:
            if self.vehicle.carrier_id != self.carrier_id:
                errors["vehicle"] = (
                    "Selected vehicle does not belong to the assigned carrier."
                )

        # 5. Optional: Prevent origin and destination from being the same
        if self.origin_id and self.destination_id:
            if self.origin_id == self.destination_id:
                errors["destination"] = "Origin and destination cannot be the same."

        if errors:
            raise ValidationError(errors)

    def record_status_event(
        self, new_status, source=None, event_timestamp=None
    ) -> ShipmentStatusEvent:
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
        shipment (Shipment): The shipment this item belongs to. Deleting the shipment will also delete the item.
        asset (Asset): The asset being shipped. Deletion of the asset is protected if referenced by a shipment item.
        quantity (int): The number of units of the asset in the shipment. Must be at least 1.
        unit_weight_lb (Decimal or None): The recorded weight per unit at the time of shipment (in pounds).
            This is a snapshot for historical accuracy and may differ from the current asset weight.
        notes (str or None): Optional notes related to this shipment item (e.g., "damaged packaging").
        created_at (datetime.datetime): Timestamp when the shipment item was created.
        updated_at (datetime.datetime): Timestamp of the most recent update to the shipment item.

    Properties:
        total_weight (Decimal): Computed total weight (quantity × unit_weight_lb).

    Methods:
        clean():
            Performs model-level validation:
            - Quantity must be at least 1.
            - Unit weight must be a positive value (enforced via field-level validators).

        save(*args, **kwargs):
            Automatically snapshots the asset's current weight into `unit_weight_lb` if not already set.

    Notes:
        This model stores a denormalized unit weight to preserve historical accuracy,
        even if the asset definition changes after the shipment is recorded.
    """

    shipment = models.ForeignKey(
        "Shipment", on_delete=models.CASCADE, related_name="items"
    )
    asset = models.ForeignKey(
        "Asset", on_delete=models.PROTECT, related_name="shipment_items"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    unit_weight_lb = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Weight per unit in pounds",
        blank=True,
        null=True,
    )

    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_weight(self) -> Decimal:
        return self.quantity * self.unit_weight_lb

    def __str__(self) -> str:
        return self.asset.name

    def save(self, *args, **kwargs):
        # Only snapshot the asset's weight if unit_weight_lb is not already set
        if self.asset and self.unit_weight_lb in [None, 0]:
            self.unit_weight_lb = self.asset.weight_lb
        super().save(*args, **kwargs)

    def clean(self):
        """
        Additional validation beyond field-level checks.

        Ensures:
        - Quantity is at least 1.
        - Unit weight is a positive value.
        """
        errors = {}

        if self.quantity < 1:
            errors["quantity"] = "Quantity must be at least 1."

        if errors:
            raise ValidationError(errors)
