from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path("carriers/", views.carrier_list),
    path("carriers/<int:pk>/", views.carrier_detail),
    path("contacts/", views.carrier_contact_list),
    path("contacts/<int:pk>/", views.carrier_contact_detail),
]
