from django.core.exceptions import ValidationError
from django.db import models
from loguru import logger



class CharacterContainerField(models.OneToOneField):
    def __init__(self, **kwargs):

        kwargs.setdefault("on_delete", models.SET_NULL)
        kwargs.setdefault("null", True)
        kwargs.setdefault("related_name", "+")
        # if not isinstance(kwargs.get("to"), BaseContainer):
        #     logger.error('You must use a containers in a character')
        super().__init__(**kwargs)

class CharacterUserField(models.ForeignKey):
    def __init__(self, **kwargs):
        kwargs.setdefault("on_delete", models.CASCADE)
        kwargs.setdefault("related_name", "%(class)s_character")
        kwargs.setdefault("default", None)
        kwargs.setdefault("null", True)
        kwargs.setdefault("verbose_name", "belongs to")
        super().__init__(**kwargs)
