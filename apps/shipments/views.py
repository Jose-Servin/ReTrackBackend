from ast import List
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Carrier, CarrierContact
from .serializers import CarrierContactSerializer, CarrierSerializer
from rest_framework.generics import ListCreateAPIView


class CarrierList(ListCreateAPIView):
    queryset = Carrier.objects.all().prefetch_related("contacts")
    serializer_class = CarrierSerializer


@api_view(["GET", "PUT", "DELETE"])
def carrier_detail(request, pk) -> Response:
    carrier = get_object_or_404(Carrier, pk=pk)

    if request.method == "GET":
        serializer = CarrierSerializer(carrier)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = CarrierSerializer(carrier, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "DELETE":
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


@api_view(["GET", "POST"])
def carrier_contact_list(request) -> Response:
    if request.method == "GET":
        qs = CarrierContact.objects.all().select_related("carrier")
        serializer = CarrierContactSerializer(qs, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = CarrierContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def carrier_contact_detail(request, pk) -> Response:
    contact = get_object_or_404(CarrierContact, pk=pk)

    if request.method == "GET":
        serializer = CarrierContactSerializer(contact)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = CarrierContactSerializer(contact, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
