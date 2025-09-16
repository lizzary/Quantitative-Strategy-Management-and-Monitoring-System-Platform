import uuid
from typing import final, List

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from loguru import logger

from api.models.instance_hash_table.instance_hash_table import InstanceHashTable
from containers.models.container_label_field import ContainerCharacterField
from labels.models.base_label import BaseLabel


class BaseContainer(models.Model):
    class Meta:
        abstract = True
        verbose_name = 'default label container'
        verbose_name_plural = 'default label container'

    container_name = models.CharField(default='default name',verbose_name='default name')
    container_type = models.CharField(default='display',choices=[('display','display'),('interactable','interactable'),('both','both'),('hide','hide')],verbose_name='container type')
    container_meta = models.CharField(default='',verbose_name='Meta data')
    used_in_character = ContainerCharacterField()

    def get_instance_name(self):
        return None

    @final
    def __str__(self):
        if self.get_instance_name() is None:
            pass

        return str(self.get_instance_name())

    def clean(self):
        label_list:List[BaseLabel] = self.__get_all_label_from_container(self)
        logger.debug(label_list)
        for label in label_list:
            if label.used_in_container != self.__class__.__name__ and label.used_in_container != 'None':
                raise ValidationError(f"label <{label.label_name}: {label.label_value}> is used")

        #如果标签没有被使用过，则将其设为已使用状态
            label.used_in_container = self.__class__.__name__
            label.save()

    def save(self, *args, **kwargs):
        """
        当容器实例被创建时，自动向哈希表中添加记录
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


    def delete(self, using=None, keep_parents=False):
        """
        当容器被删除时，自动删除所有绑定的标签实例
        :param using:
        :param keep_parents:
        :return:
        """
        for field in self._meta.get_fields():
            if isinstance(field, models.OneToOneField):
                # 获取该字段关联的实例
                related_instance = getattr(self, field.name)
                if related_instance is not None:  # 检查是否已设置关联对象
                    related_instance.delete()  # 删除关联的模型实例

        #删除哈希表中的记录
        InstanceHashTable.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk
        ).delete()

        # 最后删除自身
        super().delete(using, keep_parents)

    def __get_all_label_from_container(self,container):
        label_list = []

        for container_field in container._meta.get_fields():

            #筛选非 被外键关系 的字段
            if not container_field.is_relation:
                continue

            try:
                related_name = container_field.name
                # getattr(user,related_name) 等价于 user.<related_name>，对于一个Character和Container是一对一关系，无需调用all()
                related_instance = getattr(container,related_name)
            except AttributeError:
                continue


            label_list.append(related_instance)

        return label_list