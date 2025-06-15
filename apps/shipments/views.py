from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import status
from .models import Carrier, CarrierContact
from .serializers import CarrierContactSerializer, CarrierSerializer
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
