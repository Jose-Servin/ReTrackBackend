from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"carriers", views.CarrierViewSet, basename="carrier")
router.register(r"contacts", views.CarrierContactViewSet, basename="carrier-contact")

# URLConf
urlpatterns = router.urls
