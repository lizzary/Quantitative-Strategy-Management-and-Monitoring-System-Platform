import uuid
from typing import final, List

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from api.models.instance_hash_table.instance_hash_table import InstanceHashTable
from characters.models.character_container_field import CharacterUserField
from containers.models.base_container import BaseContainer
from django.core.exceptions import ValidationError


class BaseCharacter(models.Model):
    class Meta:
        abstract = True
        verbose_name = 'default character'
        verbose_name_plural = 'default character'

    character_name = models.CharField(default='default name',verbose_name='default name')
    user = CharacterUserField(to=User)

    def get_instance_name(self):
        return None

    @final
    def __str__(self):
        if self.get_instance_name() is None:
            pass

        return str(self.get_instance_name())

    def clean(self):
        container_list:List[BaseContainer] = self.__get_all_containers_from_character(self)
        for container in container_list:
            if container.used_in_character != self.__class__.__name__ and container.used_in_character != 'None':
                raise ValidationError(f"Container <{container.container_name}> is used")

        #如果容器没有被使用过，则将其设为已使用状态
            container.used_in_character = self.__class__.__name__
            container.save()

    def save(self, *args, **kwargs):
        """
        当角色模板实例被创建时，自动向哈希表中添加记录
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
        #删除哈希表中的记录
        InstanceHashTable.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk
        ).delete()
        super().delete(*args, **kwargs)

    def __get_all_containers_from_character(self,character):
        container_list = []

        #character = ExampleCharacter2.objects.first()
        for character_field in character._meta.get_fields():

            #筛选非 被外键关系 的字段
            if not character_field.is_relation:
                continue

            try:
                related_name = character_field.name
                # getattr(user,related_name) 等价于 user.<related_name>，对于一个Character和Container是一对一关系，无需调用all()
                related_instance = getattr(character,related_name)
            except AttributeError:
                continue

            #返回的实例非BaseContainer及其子类或为空集
            if not isinstance(related_instance,BaseContainer):
                continue

            container_list.append(related_instance)

        return container_list

