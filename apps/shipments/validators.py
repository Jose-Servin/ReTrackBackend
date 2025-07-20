from django.core.validators import RegexValidator


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
