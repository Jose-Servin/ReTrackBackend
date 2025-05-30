from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Carrier, CarrierContact
from .serializers import CarrierContactSerializer, CarrierSerializer


@api_view()
def carrier_list(request) -> Response:
    qs = Carrier.objects.all().prefetch_related("contacts")
    serializer = CarrierSerializer(qs, many=True)
    return Response(serializer.data)


@api_view()
def carrier_detail(request, pk) -> Response:
    carrier = Carrier.objects.prefetch_related("contacts").get(pk=pk)
    serializer = CarrierSerializer(carrier)
    return Response(serializer.data)


@api_view()
def carrier_contact_list(request) -> Response:
    qs = CarrierContact.objects.all()
    serializer = CarrierContactSerializer(qs, many=True)
    return Response(serializer.data)
