
from api.models.register import ModelRegister
from labels.models.base_label import BaseLabel
from labels.models.label_field import LabelNameField, LabelIntegerField, LabelDateField, LabelCharField


@ModelRegister.label_register
class ExampleLabel2(BaseLabel):

    label_name = LabelNameField(default='ExampleLabel2')
    label_value = LabelIntegerField()

    def get_instance_name(self):
        return f"{self.label_name}: {self.label_value}"