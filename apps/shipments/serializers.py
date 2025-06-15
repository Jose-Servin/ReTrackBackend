from rest_framework import serializers
from .models import Carrier, CarrierContact


class SimpleCarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = [
            "id",
            "name",
            "mc_number",
        ]


class CarrierContactSerializer(serializers.ModelSerializer):
    associated_carrier = SimpleCarrierSerializer(read_only=True, source="carrier")

    class Meta:
        model = CarrierContact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "is_primary",
            "carrier",  # This field is used for creating/updating the contact
            "associated_carrier",  # This field provides a read-only reference to the carrier
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        """
        Prevent multiple primary contacts for the same carrier.

        This method runs after field-level validation and receives all validated input as `attrs`.
        It applies cross-field logic to ensure only one primary contact exists per carrier.
        """
        is_primary = attrs.get("is_primary", False)
        carrier = attrs.get("carrier")

        # If we're editing an existing contact, this will be the instance; otherwise None
        instance = getattr(self, "instance", None)

        if is_primary and carrier:
            # Look for any existing primary contact for the same carrier
            existing_primary = CarrierContact.objects.filter(
                carrier=carrier,
                is_primary=True,
            )

            # Exclude the current instance if we're editing (not creating)
            if instance:
                existing_primary = existing_primary.exclude(pk=instance.pk)

            # If another primary contact exists, block the request
            if existing_primary.exists():
                raise serializers.ValidationError(
                    {"is_primary": "This carrier already has a primary contact."}
                )

        return attrs


class SimpleCarrierContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierContact
        fields = [
            "id",
            "first_name",
            "last_name",
        ]


class CarrierSerializer(serializers.ModelSerializer):
    contacts = SimpleCarrierContactSerializer(many=True, read_only=True)

    class Meta:
        model = Carrier
        fields = [
            "id",
            "name",
            "mc_number",
            "created_at",
            "updated_at",
            "contacts",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynaically make mc_number read-only
        if getattr(self, "instance", None) is not None:
            self.fields["mc_number"].read_only = True
