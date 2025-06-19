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


plate_validator = RegexValidator(
    regex=r"^[A-Za-z0-9-]{1,20}$",
    message="Enter a valid plate number using letters, numbers, or hyphens only (no spaces or special characters).",
)
phone_validator = RegexValidator(
    regex=r"^\d{3}-?\d{3}-?\d{4}$",
    message="Enter a 10-digit phone number in format 555-123-4567 or 5551234567.",
)

sku_validator = RegexValidator(
    regex=r"^[aA][sS][tT]\d{4}$",
    message="SKU must be in the format 'AST' followed by 4 digits (e.g., AST0001).",
)


mc_number_validator = RegexValidator(
    regex=r"^[mM][cC]\d{6}$",
    message="MC number must be in the format 'MC' followed by 6 digits (e.g., MC123456).",
)


class Carrier(models.Model):
    """
    Represents a freight carrier company.

    Attributes:
        name (str): The carrier's name.
        mc_number (str): The carrier's motor carrier number.
        created_at (datetime): Timestamp when the carrier was created.
        updated_at (datetime): Timestamp when the carrier was last updated.

    Properties:
        available_drivers (int): Number of drivers linked to this carrier.
        capacity_status (str): A label describing driver availability as Under, At, or Over Capacity.
    """

    name = models.CharField(max_length=255)
    mc_number = models.CharField(max_length=50, validators=[mc_number_validator])
    # TODO: replace with FK to core.User when model is defined
    # account_managers
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()  # Triggers `clean()` before saving
        if self.mc_number:
            self.mc_number = self.mc_number.upper().strip()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

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
    Represents a point of contact for a carrier.

    Attributes:
        carrier (ForeignKey): The carrier this contact is associated with.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Unique email address for the contact.
        phone_number (PhoneNumberField): Optional phone number in US format.
        role (str): The contact's role (e.g., Owner, Dispatch, Billing, Safety).
        is_primary (bool): Indicates if this is the primary contact for the carrier.
        created_at (datetime): Timestamp when the contact was created.
        updated_at (datetime): Timestamp when the contact was last updated.

    Constraints:
        - Only one primary contact is allowed per carrier.
        - Enforced both at the database level and through form validation via clean().
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
        phone_number (str): Optional phone number.
        email (str): Unique email address for the driver.
        carrier (ForeignKey): The carrier this driver is associated with.
        created_at (datetime): Timestamp when the driver was created.
        updated_at (datetime): Timestamp when the driver was last updated.
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
        carrier (ForeignKey): The carrier that owns or operates this vehicle.
        plate_number (str): Unique license plate identifier for the vehicle.
            - Must consist of letters, numbers, or hyphens (no spaces or symbols).
            - Accepts lowercase on input, but automatically normalized to uppercase on save.
        created_at (datetime): Timestamp when the vehicle record was created.
        updated_at (datetime): Timestamp when the vehicle record was last updated.
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
    Represents a physical item or good that can be shipped.

    Attributes:
        name (str): The name or identifier of the asset.
        slug (SlugField): A URL-friendly label used to reference the asset.
            - Automatically generated from the name if not provided.
            - Must be unique.
        description (str): Optional detailed information about the asset.
        weight_lb (Decimal): The weight of a single unit in pounds.
            - Must be greater than 0.
        length_in (Decimal): The length of the asset in inches.
        width_in (Decimal): The width of the asset in inches.
        height_in (Decimal): The height of the asset in inches.
            - All dimensions must be greater than 0.
        is_fragile (bool): Indicates whether the asset requires special handling due to fragility.
        is_hazardous (bool): Indicates whether the asset is considered hazardous material.
            - Items may be both fragile and hazardous in certain use cases.

        created_at (datetime): Timestamp when the asset was first created.
        updated_at (datetime): Timestamp of the most recent update to the asset.

    Properties:
        volume_cubic_in (Decimal): The total volume of the item in cubic inches.
        needs_special_handling (bool): True if the item is both fragile and hazardous,
            which may require custom handling, packaging, or compliance workflows.
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
        shipment (ForeignKey): The shipment associated with this event.
        status (str): The status value at this point in time (e.g., Pending, In Transit, Delivered).
        event_timestamp (datetime): When the event occurred (can be backfilled or real-time).
        source (str): Optional system or user responsible for the event.
        notes (str): Optional note related to a particular event.
        created_at (datetime): When the record was created.
        updated_at (datetime): When the record was last updated.

    Constraints:
        - (shipment, status, event_timestamp) must be unique.
        - Events are ordered chronologically by event_timestamp.

    Validation:
        - Ensures new events are not recorded with timestamps earlier than the latest event
            for the same shipment (chronological integrity).
        - Proactively checks for duplicates and raises a friendly validation error before
            database-level constraints are triggered.

    Notes:
        This model serves as the single source of truth for tracking all status changes
        in a shipment's lifecycle. Validation occurs both at the model level (via clean)
        and at the database level (via UniqueConstraint) to ensure consistency and enforce business rules.
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
        origin (ForeignKey): The origin location of the shipment.
        destination (ForeignKey): The destination location of the shipment.
        scheduled_pickup (datetime): Planned pickup time.
        scheduled_delivery (datetime): Planned delivery time.
        actual_pickup (datetime): Actual pickup time, inferred from status events.
        actual_delivery (datetime): Actual delivery time, inferred from status events.
        carrier (ForeignKey): The carrier responsible for the shipment.
        driver (ForeignKey): The assigned driver.
        vehicle (ForeignKey): The assigned vehicle.
        created_at (datetime): Timestamp when the shipment was created.
        updated_at (datetime): Timestamp when the shipment was last updated.

    Properties:
        current_status (str): The most recent shipment status, derived from related status events.

    Methods:
        record_status_event(): Logs a new ShipmentStatusEvent and updates actual pickup/delivery timestamps as needed.

    Validation:
        - Ensures scheduled delivery does not occur before scheduled pickup.
        - Ensures actual delivery does not occur before actual pickup.

    Meta:
        Default ordering is by scheduled pickup time (ascending).
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
        shipment (ForeignKey): The shipment this item belongs to.
            - Deleting the shipment will also delete this item.
        asset (ForeignKey): The asset being shipped.
            - Protected to prevent deletion if referenced by any shipment item.
        quantity (int): The number of units of the asset included in the shipment.
            - Must be 1 or greater.
        unit_weight_lb (Decimal): The recorded weight per unit at the time of shipment, in pounds.
            - Must be a positive number.
            - This is intended to be a snapshot of the asset's weight at the time of shipment.
        notes (str): Optional notes related to this shipment item (e.g., "damaged packaging").

    Properties:
        total_weight (Decimal): The total weight for this line item (quantity * unit weight).

    Validation:
        - Quantity must be at least 1.
        - Unit weight must be greater than 0.
        - These checks are enforced via field-level validators and a clean() method for better messaging.

    Notes:
        This model stores a denormalized unit weight to preserve historical accuracy,
        even if the asset's weight changes in the future.
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
    )

    notes = models.TextField(blank=True, null=True)

    @property
    def total_weight(self) -> Decimal:
        return self.quantity * self.unit_weight_lb

    def __str__(self) -> str:
        return self.asset.name

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

        if self.unit_weight_lb <= 0:
            errors["unit_weight_lb"] = "Unit weight must be a positive value."

        if errors:
            raise ValidationError(errors)
