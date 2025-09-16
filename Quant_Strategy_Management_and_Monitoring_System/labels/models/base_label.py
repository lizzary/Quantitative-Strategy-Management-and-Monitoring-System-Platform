from django.contrib.contenttypes.models import ContentType
from django.db import models
from typing import final
from abc import abstractmethod

from api.event.event_engine import EventBus
from api.event.null_event_engine import NullEventBus
from api.models.instance_hash_table.instance_hash_table import InstanceHashTable
from api.models.register import ModelRegister
from labels.models.label_field import LabelNameField, LabelTextField, LabelChoiceField, LabelUUIDField, \
    LabelsContainerField, LabelDisplayFormatField

eventBus = NullEventBus()

class BaseLabel(models.Model):
    """
    标签的抽象基类，只能通过重写来实现自定义标签
    """

    class Meta:
        abstract = True
        verbose_name = "label"
        verbose_name_plural = "label"

    label_name = LabelNameField(default='')
    label_value = LabelTextField(default='')
    label_type = LabelChoiceField(default='read_only')
    label_display_format = LabelDisplayFormatField()
    used_in_container = LabelsContainerField()


    def get_instance_name(self):
        return None

    @final
    def __str__(self):
        if self.get_instance_name() is None:
            pass

        return str(self.get_instance_name())

    @final
    def get_name(self):
        if not hasattr(self, 'label_name'):
            raise AttributeError(f"Your label {self} must have a label_name attribute")
        return self.label_name

    @final
    def get_value(self):
        if not hasattr(self, 'label_value'):
            raise AttributeError(f"Your label {self} must have a label_value attribute")
        return self.label_value

    def trigger_0(self):
        pass

    def trigger_1(self):
        pass

    def save(self, *args, **kwargs):
        """
        当标签实例被创建时，自动向哈希表中添加记录
        :param args:
        :param kwargs:
        :return:
        """

        is_new = self._state.adding  # 检查是否是新建实例
        super().save(*args, **kwargs)

        if is_new:
            InstanceHashTable.objects.create(
                content_object=self
            )
    
    def delete(self, *args, **kwargs):

        InstanceHashTable.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk
        ).delete()
        super().delete(*args, **kwargs)
