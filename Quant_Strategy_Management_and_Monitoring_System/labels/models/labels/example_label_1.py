
from api.models.register import ModelRegister
from labels.models.base_label import BaseLabel
from labels.models.label_field import LabelNameField, LabelIntegerField


@ModelRegister.label_register
class ExampleLabel1(BaseLabel):

    label_name = LabelNameField(default='ExampleLabel1')
    label_value = LabelIntegerField()

    def get_instance_name(self):
        return f"{self.label_name}: {self.label_value}"