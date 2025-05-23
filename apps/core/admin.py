from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.contrib.contenttypes.admin import GenericTabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from ..shipments.admin import ShipmentAdmin
from ..shipments.models import Shipment
from ..attachments.models import Attachment
from . import models

admin.site.unregister(Group)


@admin.register(models.User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


class AttachmentInline(GenericTabularInline):
    model = Attachment
    extra = 0
    min_num = 1


class CustomShipmentAdmin(ShipmentAdmin, ModelAdmin):
    """
    Custom admin for the Shipments model to include Attachment management.

    Inherits from the standard ShipmentAdmin but adds the AttachmentInline to manage
    attachments directly from the Shipment admin page.

    Attributes:
    - inlines (list): List of inline models to be displayed on the Shipment admin page.
    """

    inlines = [AttachmentInline]


# Unregister the default admin for the Shipment model and register a custom one with AttachmentInline support
admin.site.unregister(Shipment)
admin.site.register(Shipment, CustomShipmentAdmin)
