from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
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
    phone_number = PhoneNumberField(region="US", allow_null=True, required=False)

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
            "carrier",
            "associated_carrier",
            "created_at",
            "updated_at",
        ]


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

    def update(self, instance, validated_data):
        if "mc_number" in validated_data:
            raise serializers.ValidationError(
                {"mc_number": "This field cannot be updated once set."}
            )
        return super().update(instance, validated_data)
