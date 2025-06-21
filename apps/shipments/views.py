from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import status
from .models import (
    Carrier,
    CarrierContact,
    Driver,
    Vehicle,
    Asset,
    Shipment,
    ShipmentItem,
)
from .serializers import (
    CarrierContactSerializer,
    CarrierSerializer,
    DriverSerializer,
    VehicleSerializer,
    AssetSerializer,
    ShipmentSerializer,
    ShipmentItemSerializer,
)
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet


class CarrierViewSet(ModelViewSet):
    """
    ViewSet for managing carriers.
    Provides list, create, retrieve, update, and delete operations.
    """

    queryset = Carrier.objects.all().prefetch_related("contacts").order_by("id")
    serializer_class = CarrierSerializer

    def destroy(self, request, pk) -> Response:
        carrier = get_object_or_404(Carrier, pk=pk)
        driver_cnt = carrier.drivers.count()
        vehicle_cnt = carrier.vehicles.count()
        contact_cnt = carrier.contacts.count()

        if contact_cnt > 0 or driver_cnt > 0 or vehicle_cnt > 0:
            return Response(
                {
                    "error": "Cannot delete carrier with associated records.",
                    "contacts": contact_cnt,
                    "drivers": driver_cnt,
                    "vehicles": vehicle_cnt,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        carrier.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CarrierContactViewSet(ModelViewSet):
    """
    ViewSet for managing carrier contacts.
    Provides list, create, retrieve, update, and delete operations.
    """

    queryset = CarrierContact.objects.all().select_related("carrier").order_by("id")
    serializer_class = CarrierContactSerializer

    def destroy(self, request, pk) -> Response:
        contact = get_object_or_404(CarrierContact, pk=pk)
        if contact.is_primary:
            return Response(
                {"error": "Cannot delete primary contact."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DriverViewSet(ModelViewSet):
    """
    ViewSet for managing drivers.
    Provides list, create, retrieve, update, and delete operations.
    """

    queryset = Driver.objects.all().select_related("carrier").order_by("id")
    serializer_class = DriverSerializer


class VehicleViewSet(ModelViewSet):
    """
    ViewSet for managing vehicles.
    Provides list, create, retrieve, update, and delete operations.
    """

    queryset = Vehicle.objects.all().select_related("carrier").order_by("id")
    serializer_class = VehicleSerializer


class AssetViewSet(ModelViewSet):
    """
    ViewSet for managing assets.
    Provides list, create, retrieve, update, and delete operations.
    """

    queryset = Asset.objects.all().order_by("id")
    serializer_class = AssetSerializer


class ShipmentViewSet(ModelViewSet):
    """
    ViewSet for managing shipments.
    Provides list, create, retrieve, update, and delete operations.
    """

    queryset = (
        Shipment.objects.all()
        .select_related("carrier", "driver", "vehicle")
        .order_by("id")
    )
    serializer_class = ShipmentSerializer


class ShipmentItemViewSet(ModelViewSet):
    """
    ViewSet for managing shipment items.
    Provides list, create, retrieve, update, and delete operations.
    """

    queryset = (
        ShipmentItem.objects.all().select_related("shipment", "asset").order_by("id")
    )
    serializer_class = ShipmentItemSerializer
