from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"carriers", views.CarrierViewSet, basename="carrier")
router.register(r"contacts", views.CarrierContactViewSet, basename="carrier-contact")
router.register(r"drivers", views.DriverViewSet, basename="driver")
router.register(r"vehicles", views.VehicleViewSet, basename="vehicle")
router.register(r"assets", views.AssetViewSet, basename="asset")

# URLConf
urlpatterns = router.urls
