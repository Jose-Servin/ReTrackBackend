from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r"carriers", views.CarrierViewSet, basename="carrier")
router.register(r"contacts", views.CarrierContactViewSet, basename="carrier-contact")
router.register(r"drivers", views.DriverViewSet, basename="driver")
router.register(r"vehicles", views.VehicleViewSet, basename="vehicle")
router.register(r"assets", views.AssetViewSet, basename="asset")
router.register(r"shipments", views.ShipmentViewSet, basename="shipment")
router.register(r"shipment-items", views.ShipmentItemViewSet, basename="shipment-item")

# Nested Shipment Status Events router

shipments_router = routers.NestedDefaultRouter(router, "shipments", lookup="shipment")
shipments_router.register(
    "status", views.ShipmentStatusEventViewSet, basename="shipment-status"
)

# URLConf
urlpatterns = router.urls + shipments_router.urls
