from ast import List
from webbrowser import get
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Carrier, CarrierContact
from .serializers import CarrierContactSerializer, CarrierSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class CarrierList(ListCreateAPIView):
    queryset = Carrier.objects.all().prefetch_related("contacts")
    serializer_class = CarrierSerializer


class CarrierDetail(RetrieveUpdateDestroyAPIView):
    queryset = Carrier.objects.all().prefetch_related("contacts")
    serializer_class = CarrierSerializer

    def delete(self, request, pk) -> Response:
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


class CarrierContactList(ListCreateAPIView):
    queryset = CarrierContact.objects.all().select_related("carrier")
    serializer_class = CarrierContactSerializer


class CarrierContactDetail(RetrieveUpdateDestroyAPIView):
    queryset = CarrierContact.objects.all().select_related("carrier")
    serializer_class = CarrierContactSerializer
