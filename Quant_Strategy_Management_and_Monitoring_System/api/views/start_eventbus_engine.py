import traceback

from django.contrib.auth.models import User
from django.db.models import QuerySet
from loguru import logger
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.event.eventbus_object_pool import EventBusObjectPool
from characters.models.base_character import BaseCharacter
from containers.models.base_container import BaseContainer
from labels.models.base_label import BaseLabel
from labels.models.label_trigger_manager import LabelTriggerManager


class StartEventBusEngine(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_id = self.request.user.id
        user = User.objects.get(id=user_id)
        try:
            eventbus = EventBusObjectPool.get_for_user(user_id)

            for character_instance in self.__get_all_characters_from_user(user):
                for container_instance in self.__get_all_containers_from_character(character_instance):
                    for label_instance in self.__get_all_label_from_container(container_instance):
                        LabelTriggerManager.install_instance(label_instance)

            LabelTriggerManager.install_to_eventbus(eventbus)


            return Response({"message":f'event engine of user id {user_id} started'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(e)
            return Response({'error': traceback.format_exc()}, status=status.HTTP_400_BAD_REQUEST)

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