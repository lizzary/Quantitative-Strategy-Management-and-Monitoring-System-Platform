import sys
import traceback

from django.contrib.auth.models import User
from django.db.models import QuerySet
from loguru import logger
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


from api.models.instance_hash_table.instance_hash_table import InstanceHashTable
from characters.models.base_character import BaseCharacter
from containers.models.base_container import BaseContainer
from labels.models.base_label import BaseLabel


class UserCharactersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self):
        super().__init__()

        self.character_instance_list = []

    def get(self, request):

        characters = []

        user_id = self.request.user.id

        user = User.objects.get(id=user_id)

        for character in self.__get_all_characters_from_user(user):
            character_uid = InstanceHashTable.get_uuid_for_instance(character)

            data = dict()
            data['uuid'] = character_uid
            data['character_template_name'] = character.character_name
            data['containers'] = []

            logger.info(f'searching character, {str(character)}: uid={character_uid}')

            for container in self.__get_all_containers_from_character(character):
                container_uid = InstanceHashTable.get_uuid_for_instance(container)

                container_doc = dict()
                container_doc['uuid'] = container_uid
                container_doc['container_name'] = container.container_name
                container_doc['container_type'] = container.container_type
                container_doc['container_meta'] = container.container_meta
                container_doc['labels'] = []


                logger.info(f'|__________> searching container, {str(container)}: uid={container_uid}')

                for label in self.__get_all_label_from_container(container):
                    label_uid = InstanceHashTable.get_uuid_for_instance(label)

                    label_doc = dict()
                    label_doc['uuid'] = label_uid
                    label_doc['label_name'] = label.label_name
                    label_doc['label_value'] = label.label_value
                    label_doc['label_type'] = label.label_type
                    container_doc['labels'].append(label_doc)

                    logger.info(f'              |__________> searching label, {str(label)}: uid={label_uid}')

                data['containers'].append(container_doc)

            characters.append(data)

        return Response(characters,status=status.HTTP_200_OK)

    def __get_all_characters_from_user(self,user:User):
        character_list = []
        for user_field in user._meta.get_fields():

            #筛选非 被外键关系 的字段
            if not user_field.is_relation:
                continue

            try:
                related_name = user_field.name
                # getattr(user,related_name).all() 等价于 user.<related_name>.all()，对于一个User可以对多个Character，需要调用all()来获取所有Character实例
                related_instance_list:QuerySet = getattr(user,related_name).all()
            except AttributeError:
                continue

            #返回的查询集非BaseCharacter及其子类或为空集
            if not isinstance(related_instance_list.first(),BaseCharacter):
                continue

            for character in related_instance_list:
                character_list.append(character)

        return character_list

    def __get_all_containers_from_character(self,character:BaseCharacter):
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

    def __get_all_label_from_container(self,container:BaseContainer):
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

            #返回的实例非BaseLabel及其子类或为空集
            if not isinstance(related_instance,BaseLabel):
                continue

            label_list.append(related_instance)

        return label_list
