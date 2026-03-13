from django.db import models


class ActivateableModel(models.Model):
    is_active = models.BooleanField('有効', default=True)

    class Meta:
        abstract = True
