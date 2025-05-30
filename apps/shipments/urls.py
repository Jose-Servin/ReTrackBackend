from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path("carriers/", views.carrier_list),
    path("carriers/<int:pk>/", views.carrier_detail),
    path("carrier-contact/", views.carrier_contact_list),
]
