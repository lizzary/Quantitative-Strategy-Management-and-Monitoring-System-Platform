from typing import Callable, Union, List

from loguru import logger

from api.event.event_engine import EventBus
from labels.models.base_label import BaseLabel


class LabelTriggerManager:
    """
    记录所有标签的所属类名和触发器，对于所有用户来说，标签触发器的行为都应保持一致，因此该trigger_hash_tabel是全局共享的，
    同时也不应使用trigger_hash_tabel中"instance"的值（因为该值可能已经被其它用户的install_instance()方法覆盖）
    {
    "<class_name>": {
        "instance": <BaseLabel> or None
        "trigger_0": {
            "func": <callable>,
            "listener_args": {
                "listener_type": <int>,
                "listen_event": str or List[str] or None,
                "delay": <int> or None
            },
            "publish": <str>
        },
        "trigger_1": {
            "func": <callable>,
            "listener_args": {
                "listener_type": <int>,
                "listen_event": <str> or <List[str]> or None,
                "delay": <int> or None
            }
            "publish": <str>
        }
    },
    "<class_name 2>": {}
    }
    """
    trigger_hash_tabel = dict()

    @staticmethod
    def call(label_instance:BaseLabel,action:str):
        if not isinstance(label_instance,BaseLabel):
            logger.critical(f'LABELTRIGGER: You seems try to call a trigger with an non BaseLabel instance <{label_instance}>')
            return None

        logger.debug(LabelTriggerManager.trigger_hash_tabel)
        label_class_name = label_instance.__class__.__name__
        LabelTriggerManager.trigger_hash_tabel[label_class_name][action]["func"](label_instance)

    @staticmethod
    def register_trigger(
            listener_type:int = EventBus.NONE,
            listen_event:Union[str, List[str]] = None,
            publish:str=None,
            delay:int=None
    ):
        def decorator(func: Callable):
            func_class_name = func.__qualname__.split('.')[0] #<class_name>.<func name> => <class_name>
            func_name = func.__name__ #<class_name>.<func name> => <func name>

            if func_class_name not in LabelTriggerManager.trigger_hash_tabel:
                LabelTriggerManager.trigger_hash_tabel[func_class_name] = {}
            LabelTriggerManager.trigger_hash_tabel[func_class_name]["instance"] = None
            LabelTriggerManager.trigger_hash_tabel[func_class_name][func_name] = dict({
                "func": func,
                "listener_args": {
                    "listener_type": listener_type,
                    "listen_event": listen_event,
                    "delay": delay
                },
                "publish": publish
            })

            logger.success(f"LABELTRIGGER: Registered <{func_class_name}.{func_name}>, detail: {{{func_class_name}:{LabelTriggerManager.trigger_hash_tabel[func_class_name]}}}")
            return func

        return decorator

    @staticmethod
    def install_instance(instance:BaseLabel):
        """
        将指定实例安装到trigger_hash_tabel中所属类的"instance"字段下
        :param instance:
        :return:
        """

        if not isinstance(instance,BaseLabel):
            logger.critical(f'LABELTRIGGER: You seems try to install an non BaseLabel instance {instance} in eventBus')
            return None


        label_class_name = instance.__class__.__name__

        if label_class_name not in LabelTriggerManager.trigger_hash_tabel:
            return None

        LabelTriggerManager.trigger_hash_tabel[label_class_name]["instance"] = instance


    @staticmethod
    def install_to_eventbus(eventBus:EventBus):
        """
        该函数建议在install_instance()方法之后调用
        1. 遍历整个trigger_hash_tabel，提取"instance"字段中的标签实例并将其作为触发器函数的参数
        2. 将带有函数参数的触发器打包为一个lambda函数
        3. 将这个lambda函数和根据trigger_hash_tabel中的监听器信息注册到提供的eventBus实例中
        3.1. 如果触发器需要在调用后发布事件（publish不为空），则将经过eventBus.publish_event修饰后的可调用对象写入trigger_hash_tabel中的"func”字段
        4. （重要）不应再使用trigger_hash_tabel中的"instance"字段的值，因为该值不再有效
        :param eventBus:
        :return:
        """
        if eventBus.is_install:
            logger.warning('This event bus is already installed')
            return None
        else:
            eventBus.is_install = True

        for class_name,triggers_info in LabelTriggerManager.trigger_hash_tabel.items():

            #BaseLabel实例
            instance = triggers_info["instance"]

            if not isinstance(instance, BaseLabel):
                logger.critical(
                    f'LABELTRIGGER: You seems try to use an non BaseLabel instance {instance} in eventBus')
                return None

            for trigger_type,trigger in triggers_info.items():

                if trigger_type != "trigger_0" and trigger_type != "trigger_1":
                    continue

                #该回调是否需要在结束是发布事件
                publish = trigger["publish"]

                current_trigger = trigger  # 保存当前状态
                if publish is not None:
                    """
                    publish不为空
                    使用装饰器修饰需要在结束时发布事件的回调
                    eventBus.publish_event(<类名>.<触发器类型>)返回一个decorator(func: Callable)函数
                    该函数被传入一个lambda函数作为回调函数：lambda(t=current_trigger, inst=instance) : t["func"](inst)
                    """
                    # 装饰原始函数并更新到哈希表
                    trigger["func"] = eventBus.publish_event(publish)(current_trigger["func"])
                    # 将instance变量传入
                    callback = lambda t=current_trigger, inst=instance: t["func"](inst)
                else:
                    """
                    publish为空
                    """
                    callback = lambda t=current_trigger, inst=instance: t["func"](inst)

                listener_args = trigger["listener_args"]
                listener_type = listener_args["listener_type"]
                listen_event = listener_args["listen_event"]
                delay = listener_args["delay"]

                if listener_type == EventBus.IMMEDIATE:
                    eventBus.add_immediate_listener(
                        source=listen_event,
                        callback=callback
                    )

                if listener_type == EventBus.DELAY:
                    eventBus.add_delayed_listener(
                        source=listen_event,
                        delay=delay,
                        callback=callback,
                    )

                if listener_type == EventBus.JOINT:
                    eventBus.add_joint_listener(
                        sources=listen_event,
                        callback=callback
                    )

                if listener_type == EventBus.PATTERN:
                    eventBus.add_pattern_listener(
                        pattern=listen_event,
                        callback=callback
                    )








