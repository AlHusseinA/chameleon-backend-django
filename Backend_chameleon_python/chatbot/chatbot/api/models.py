from django.db import models
import uuid

class Conversation(models.Model):
    # these are the field that will be stored in db
    uuid= models.UUIDField(default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True)
    messages = models.JSONField()



