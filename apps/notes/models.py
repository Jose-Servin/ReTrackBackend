from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class AttachedNoteManager(models.Manager):
    """
    Custom manager for AttachedNote to query notes for any object.
    """

    def get_notes_for(self, obj_type, object_id):
        """
        Retrieve all notes associated with a specific object.

        Parameters:
        - obj_type (Model class): The model class of the object.
        - obj_id (int): The primary key of the object.

        Returns:
        - QuerySet: A queryset containing AttachedNote instances related to the given object.
        """
        content_type = ContentType.objects.get_for_model(obj_type)
        queryset = AttachedNote.objects.select_related("note").filter(
            content_type=content_type, object_id=object_id
        )

        return queryset


class Note(models.Model):
    """
    Represents a note that can be attached to any object.

    Attributes:
    - body (str): The content of the note.

    Methods:
    - __str__(): Returns the body of the note.
    """

    body = models.CharField(max_length=255)

    def __str__(self) -> str:
        """
        Returns a string representation of the note.
        """
        return self.body


class AttachedNote(models.Model):
    """
    Represents a note attached to a specific object via a generic relation.

    Attributes:
    - note (ForeignKey): The note associated with the object.
    - content_type (ForeignKey): The type of the related object.
    - object_id (int): The ID of the related object.
    - content_object (GenericForeignKey): The actual object that the note is associated with.

    Notes:
    - Uses a GenericForeignKey to allow attaching a note to any model instance.
    - Deleting an object will also delete all associated notes.
    - Assumes that the related object has an integer primary key.
    """

    objects = AttachedNoteManager()

    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    # Generic relationship
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    # The actual object the note is attached to (Shipment, Carrier, etc.)
    content_object = GenericForeignKey()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note attached to {self.content_type} ({self.object_id})"
