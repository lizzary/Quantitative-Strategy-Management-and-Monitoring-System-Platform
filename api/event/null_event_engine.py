from typing import Callable, List, Dict, Set, Deque, Optional

from loguru import logger

from api.event.event_engine import EventBus


class NullEventBus(EventBus):
    """
    该类是EventBus需要是一个初始值或null值时的实现
    """
    def __init__(self):
        super().__init__()

    def publish(self,event: str):
        logger.critical(f"NullEventBus: You are trying to use a NULL evnetBus object with evnet={event}!")

    def process_one_step(self):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )

    def process(self, maxStep=10000):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )

    def add_immediate_listener(self, source: str, callback: Callable):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )

    def add_delayed_listener(self, source: str, delay: int, callback: Callable):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )

    def add_joint_listener(self, sources: List[str], callback: Callable):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )

    def add_pattern_listener(self, pattern: List[str], callback: Callable):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )

    def publish_event(self, event: str):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )

    def listen_immediately(self, source: str):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )

    def listen_delayed(self, source: str, delay: int):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )

    def listen_jointly(self, sources: List[str]):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )

    def listen_pattern_matcher(self, pattern: List[str]):
        logger.critical(
            f"NullEventBus: You are trying to use a NULL evnetBus object nothing will happen!"
        )



