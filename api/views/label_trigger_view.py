import uuid

from loguru import logger
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.event.eventbus_object_pool import EventBusObjectPool
from api.models.instance_hash_table.instance_hash_table import InstanceHashTable
from labels.models.base_label import BaseLabel
from labels.models.label_trigger_manager import LabelTriggerManager


class LabelTriggerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user_id = self.request.user.id

        query_paras = self.request.query_params.dict()
        logger.debug(query_paras)

        if 'label_uuid' not in query_paras or 'trigger' not in query_paras:
            return Response({"parameter require: 'label_uuid' and 'trigger'"}, status=status.HTTP_400_BAD_REQUEST)

        if query_paras['trigger'] != '0' and query_paras['trigger'] != '1':
            return Response({"parameter error: 'trigger' must be '0' or '1'"}, status=status.HTTP_400_BAD_REQUEST)

        if not EventBusObjectPool.exist(user_id):
            return Response({"eventbus error": "you must GET /api/start-event-engine first"}, status=status.HTTP_400_BAD_REQUEST)

        label_uuid = query_paras['label_uuid']
        trigger = query_paras['trigger']
        eventbus = EventBusObjectPool.get_for_user(user_id)

        label_instance:BaseLabel = InstanceHashTable.get_instance_by_uuid(label_uuid)

        if label_instance is None or not isinstance(label_instance, BaseLabel):
            return Response({"uuid error": f"cannot find a label using your uuid {label_uuid}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if trigger == '0':
                LabelTriggerManager.call(label_instance,'trigger_0')
            if trigger == '1':
                LabelTriggerManager.call(label_instance,'trigger_1')
            eventbus.process()
            return Response({"user_id":user_id, "label_uid":label_uuid, "message": "label successfully trigger"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(e)
            return Response({"trigger error": str(e)}, status=status.HTTP_400_BAD_REQUEST)






