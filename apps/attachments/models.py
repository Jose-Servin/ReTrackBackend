from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings


class AttachmentManager(models.Manager):
    """
    Manager for the Attachment model.

    Methods:
    - get_attachments_for(obj_type, obj_id): Returns all attachments linked to the given model class and object ID.

    Notes:
    - Useful when the model class and primary key are known (e.g., from a serializer).
    - Assumes related objects use integer primary keys.
    """

    def get_attachments_for(self, obj_type, obj_id):
        """
        Returns all attachments linked to the specified model class and object ID.

        Args:
        - obj_type (Model): The model class (e.g., Shipment).
        - obj_id (int): The primary key of the object to fetch attachments for.

        Returns:
        - QuerySet of Attachment instances.
        """
        content_type = ContentType.objects.get_for_model(obj_type)
        return self.filter(content_type=content_type, object_id=obj_id)


class Attachment(models.Model):
    """
    Represents a file attachment that can be associated with any object.

    Attributes:
    - file (FileField): The uploaded file.
    - uploaded_by (ForeignKey): The user who uploaded the file.
    - description (TextField): Optional descriptive text for the attachment.
    - content_type (ForeignKey): The type of the related object.
    - object_id (int): The ID of the related object.
    - content_object (GenericForeignKey): The actual object that the file is attached to.
    - uploaded_at (DateTimeField): Timestamp of when the file was uploaded.

    Notes:
    - Uses a GenericForeignKey to allow file attachments to any model instance.
    - Can be used for documents like invoices, proof of delivery, or images.
    - Assumes related models use integer primary keys.
    """

    objects = AttachmentManager()

    file = models.FileField(upload_to="attachments/%Y/%m/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    description = models.TextField(blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.file.name} attached to {self.content_type} {self.object_id}"
