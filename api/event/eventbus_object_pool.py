import threading

from loguru import logger

from api.event.event_engine import EventBus
from typing import Callable, Dict, Set


class EventBusObjectPool:
    #{"<用户id>": <EventBus实例>, ... }
    eventBusObjectPool: Dict[str, 'EventBus'] = dict()
    pool_lock = threading.RLock()  # 线程安全锁

    @staticmethod
    def get_for_user(user_id:int):
        user_id = str(user_id)
        with EventBusObjectPool.pool_lock:  # 获取锁
            if user_id not in EventBusObjectPool.eventBusObjectPool:
                # 在锁保护下创建和插入
                new_bus = EventBus()
                EventBusObjectPool.eventBusObjectPool[user_id] = new_bus
            return EventBusObjectPool.eventBusObjectPool[user_id]


    @staticmethod
    def exist(user_id:int):
        user_id = str(user_id)
        logger.debug(EventBusObjectPool.eventBusObjectPool)
        return user_id in EventBusObjectPool.eventBusObjectPool