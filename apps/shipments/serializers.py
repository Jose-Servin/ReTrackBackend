from rest_framework import serializers
from .models import Carrier, CarrierContact


class CarrierContactSerializer(serializers.ModelSerializer):
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
            "created_at",
            "updated_at",
        ]


class CarrierSerializer(serializers.ModelSerializer):
    # TODO:Prevent updating mc_number
    contacts = CarrierContactSerializer(many=True, read_only=True)

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
