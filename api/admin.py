from django.contrib import admin
from loguru import logger

from api.models.instance_hash_table.instance_hash_table import InstanceHashTable
# Register your models here.
from api.models.register import ModelRegister
from rest_framework.authtoken.models import Token



"""
使用默认管理模型（admin.ModelAdmin）批量注册LabelsRegister.register_labels内的标签
"""
@admin.register(*ModelRegister.registered_labels)
class ModelNameAdmin(admin.ModelAdmin):
    fields = ('label_name', 'label_value', 'label_type','label_display_format','used_in_container')  # 按顺序显示这些字段

    def get_model_perms(self, request):
        # 返回空字典，确保模型不在左侧导航显示
        return {}

@admin.register(*ModelRegister.registered_containers)
class ContainerAdmin(admin.ModelAdmin):
    # fields = ('container_name', 'container_type', 'container_meta', 'used_in_character')  # 按顺序显示这些字段

    def delete_queryset(self, request, queryset):
        for instance in queryset:
            instance.delete()



@admin.register(*ModelRegister.registered_characters,InstanceHashTable)
class CharacterAdmin(admin.ModelAdmin):

    def delete_queryset(self, request, queryset):
        for instance in queryset:
            instance.delete()

admin.register(Token)


