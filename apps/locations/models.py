from django.db import models


class Location(models.Model):
    """
    Represents a physical location used in shipments.

    Attributes:
        name (str): Human-friendly label (e.g., 'Houston Terminal', 'Warehouse 12').
        address_line1 (str): Street address line 1.
        address_line2 (str): Optional second line (e.g., suite or unit).
        city (str): City name.
        state (str): State or province abbreviation (e.g., 'TX').
        postal_code (str): ZIP or postal code.
        country (str): ISO country code (e.g., 'US').
        latitude (Decimal): Optional latitude for mapping.
        longitude (Decimal): Optional longitude for mapping.
        created_at (datetime): Timestamp when the location was created.
        updated_at (datetime): Timestamp when the location was last updated.
    """

    name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
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

    def __str__(self) -> str:
        return self.name
