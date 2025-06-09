from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path("carriers/", views.CarrierList.as_view()),
    path("carriers/<int:pk>/", views.CarrierDetail.as_view()),
    path("contacts/", views.CarrierContactList.as_view()),
    path("contacts/<int:pk>/", views.CarrierContactDetail.as_view()),
]
