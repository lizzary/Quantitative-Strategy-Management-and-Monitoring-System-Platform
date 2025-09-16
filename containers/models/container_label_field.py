from django.core.exceptions import ValidationError
from django.db import models
from loguru import logger




class ContainerLabelField(models.OneToOneField):
    def __init__(self, **kwargs):

        kwargs.setdefault("on_delete", models.SET_NULL)
        kwargs.setdefault("null", True)
        kwargs.setdefault("related_name", "+")
        # if not isinstance(kwargs.get("to"), BaseLabel):
        #     logger.error('You must use a label in a container')

        super().__init__(**kwargs)


class ContainerCharacterField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'belongs to')
        kwargs.setdefault('default', 'None')
        kwargs.setdefault('help_text', 'This value is automatically managed by the system to prevent the label from being reused across models. Please do not modify this value unless necessary.')
        super().__init__(*args, **kwargs)

