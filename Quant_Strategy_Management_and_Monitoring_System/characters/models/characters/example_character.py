
from api.models.register import ModelRegister
from characters.models.base_character import BaseCharacter
from characters.models.character_container_field import CharacterContainerField
from containers.models.container.example_container_1 import ExampleContainer


@ModelRegister.character_register
class ExampleCharacter(BaseCharacter):

    class Meta:
        verbose_name = 'ExampleCharacter'
        verbose_name_plural = 'ExampleCharacter'

    container = CharacterContainerField(to=ExampleContainer,verbose_name='ExampleContainer')

    def get_instance_name(self):
        return f"{self.character_name}"