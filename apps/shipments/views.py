from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Carrier, CarrierContact
from .serializers import CarrierContactSerializer, CarrierSerializer


@api_view(["GET", "POST"])
def carrier_list(request) -> Response:
    if request.method == "GET":
        qs = Carrier.objects.all().prefetch_related("contacts")
        serializer = CarrierSerializer(qs, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = CarrierSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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


@api_view()
def carrier_contact_list(request) -> Response:
    qs = CarrierContact.objects.all()
    serializer = CarrierContactSerializer(qs, many=True)
    return Response(serializer.data)
