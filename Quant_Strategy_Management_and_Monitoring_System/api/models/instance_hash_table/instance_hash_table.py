import uuid

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class InstanceHashTable(models.Model):

    class Meta:
        verbose_name = 'Instance Hash Table'
        verbose_name_plural = 'Instance Hash Table'


    hash_value = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='哈希ID',db_index=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


    @staticmethod
    def get_uuid_for_instance(instance):
        """
        获取指定实例在哈希表中的UUID

        参数:
            instance: 任意模型实例

        返回:
            UUID字符串 (如果存在)
            None (如果不存在记录)
        """
        # 1. 获取实例的ContentType
        content_type = ContentType.objects.get_for_model(instance)

        # 2. 查询哈希表记录
        try:
            record = InstanceHashTable.objects.get(
                content_type=content_type,
                object_id=instance.pk
            )
            return str(record.hash_value)

        except InstanceHashTable.DoesNotExist:
            return None

    @staticmethod
    def get_instance_by_uuid(uuid_str:str):
        try:
            # 将字符串转换为UUID对象（Django会自动处理）
            uuid_obj = uuid.UUID(uuid_str)

            # 获取哈希表记录
            record = InstanceHashTable.objects.get(hash_value=uuid_obj)

            # 返回关联的实际模型实例
            return record.content_object

        except (ValueError, ObjectDoesNotExist):
            # 处理无效UUID或找不到记录的情况
            return None

    def __str__(self):
        return str(f'{self.content_type}(id:{self.object_id}) : {self.hash_value}')

