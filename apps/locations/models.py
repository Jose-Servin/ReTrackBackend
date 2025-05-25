from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class Location(models.Model):
    """
    Represents a physical location used in shipments.

    Attributes:
        name (str): Human-friendly label (e.g., 'Houston Terminal', 'Warehouse 12').
        address_line1 (str): Street address line 1.
        address_line2 (str): Optional second line (e.g., suite or unit).
        city (str): City name.
        state (str): State or province abbreviation (e.g., 'TX').
        postal_code (str): ZIP or postal code (validated for US format).
        country (str): ISO country code (e.g., 'US').
        latitude (Decimal): Optional latitude for mapping.
        longitude (Decimal): Optional longitude for mapping.
        created_at (datetime): Timestamp when the location was created.
        updated_at (datetime): Timestamp when the location was last updated.

    Constraints:
        - A location must have a unique combination of name, address_line1, city, state, and postal_code.
        - A location's name must be unique within a city.
        - Postal code must follow US ZIP code format (e.g., 12345 or 12345-6789).
        - If either latitude or longitude is set, the other must also be set.

    Validation:
        - Ensures both latitude and longitude are either set or both blank.
    """

    name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\d{5}(-\d{4})?$",
                message="Enter a valid US ZIP code (e.g., 12345 or 12345-6789).",
            )
        ],
    )
    country = models.CharField(max_length=2, default="US")

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            # 123 Main St, Houston, TX 77001
            models.UniqueConstraint(
                fields=["name", "address_line1", "city", "state", "postal_code"],
                name="unique_location_identity",
            ),
            # Houston, Texas
            models.UniqueConstraint(
                fields=["name", "city"], name="unique_location_name_per_city"
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if bool(self.latitude) != bool(self.longitude):
            raise ValidationError(
                "Both latitude and longitude must be provided together."
            )
