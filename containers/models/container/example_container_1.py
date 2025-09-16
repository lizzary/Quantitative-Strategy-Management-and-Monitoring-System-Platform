from api.models.register import ModelRegister
from containers.models.base_container import BaseContainer
from containers.models.container_label_field import ContainerLabelField
from labels.models.labels.example_label_1 import ExampleLabel1
from labels.models.labels.example_label_2 import ExampleLabel2


@ModelRegister.container_register
class ExampleContainer(BaseContainer):

    class Meta:
        verbose_name = 'Example container'
        verbose_name_plural = 'Example container'



    label_1 = ContainerLabelField(to=ExampleLabel1,verbose_name='ExampleLabel1')
    label_2 = ContainerLabelField(to=ExampleLabel2,verbose_name='ExampleLabel2')

    def get_instance_name(self):
        return self.container_name