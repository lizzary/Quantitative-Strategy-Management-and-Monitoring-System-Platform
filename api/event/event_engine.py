import functools
import heapq
from collections import defaultdict
from typing import Callable, List, Dict, Set, Deque, Optional
import queue

from loguru import logger


class EventBus:

    #listener type enum
    NONE = 0
    IMMEDIATE = 1
    DELAY = 2
    JOINT = 3
    PATTERN = 4

    def __init__(self):
        self.is_install = False #该事件引擎是否被加载过
        self.event_count = 0  # 全局事件计数器
        self.event_bus = queue.Queue(maxsize=1000)

        #立即触发监听器表，{<监听事件名>:[<可调用对象 1>, <可调用对象 2>, ... }
        self.immediate_listeners: Dict[str, List[Callable]] = defaultdict(list)

        #延迟触发表，[(触发事件计数, 回调)，(触发事件计数, 回调)，...】
        self.delayed_tasks: List[tuple] = []  # 最小堆: (触发事件计数, 回调)

        #联合触发表
        self.joint_conditions: List['JointCondition'] = []

        #模式触发表
        self.pattern_matchers: List['PatternMatcher'] = []

    def publish(self,event: str):
        """发布事件，将事件放入队列末尾"""
        self.event_bus.put(event)
        logger.info(f"EVENTBUS: event <{event}> is published")

    def process_one_step(self):
        """从队列头开始处理事件"""
        if self.event_bus.empty():
            logger.success("EVENTBUS: process done !")
            return True

        if self.event_bus.full():
            logger.critical(f"EVENTBUS: Event bus full!")
            return False

        self.event_count += 1
        event = self.event_bus.get()
        logger.info(f"EVENTBUS: event <{event}> is processing")

        # 立即触发
        for callback in self.immediate_listeners[event]:
            logger.info(f"EVENTBUS: event callback <func: {callback.__name__}> is triggered")
            callback()

        # 检查延迟触发任务
        while self.delayed_tasks and self.delayed_tasks[0][0] <= self.event_count:
            _, callback = heapq.heappop(self.delayed_tasks)
            logger.info(f"EVENTBUS: event callback <func: {callback.__name__}> is triggered")
            callback()

        # 联合触发
        for condition in self.joint_conditions:
            condition.on_event(event)

        # 模式触发
        for matcher in self.pattern_matchers:
            matcher.on_event(event)

        logger.info(f"EVENTBUS: event <{event}> processing is end")

        return False

    def process(self,maxStep=10000):
        for i in range(maxStep):
            is_done = self.process_one_step()
            if is_done:
                return

        logger.critical(f"EVENTBUS: reach step limit {maxStep}, check infinite event loop")



    def add_immediate_listener(self, source: str, callback: Callable):
        """立即触发：source发生 -> 立即执行callback"""
        self.immediate_listeners[source].append(callback)

    def add_delayed_listener(self, source: str, delay: int, callback: Callable):
        """延迟触发：source发生 -> 等待delay个事件后执行callback"""

        #当source事件被发布时，该函数会被立刻调用（因为借用了立即触发器），向最小堆内压入元素：(trigger_at, callback)
        def delayed_callback_wrapper():
            trigger_at = self.event_count + delay #delay的值等于add_delayed_listener中delay参数的值（闭包）
            heapq.heappush(self.delayed_tasks, (trigger_at, callback))

        #重命名该回调函数，使其在日志中可见
        delayed_callback_wrapper.__name__ = f"delayed_wrapper_{callback.__name__}"

        self.add_immediate_listener(source, delayed_callback_wrapper)

    def add_joint_listener(self, sources: List[str], callback: Callable):
        """联合触发：所有sources都发生（无视顺序）-> 执行callback"""
        condition = JointCondition(set(sources), callback)
        self.joint_conditions.append(condition)

    def add_pattern_listener(self, pattern: List[str], callback: Callable):
        """模式触发：事件序列匹配pattern（支持'*'通配）-> 执行callback"""
        matcher = PatternMatcher(pattern, callback)
        self.pattern_matchers.append(matcher)

    """以下是装饰器版本的实现，支持使用装饰器将一个函数绑定到一个监听器的回调"""

    def publish_event(self, event: str):
        """
        事件发布的装饰器版本\n
        该装饰器须在监听器装饰器@listen_xxx之前调用（该装饰器在@listen_xx下方）
        :param event:
        :return:
        """
        def decorator(func: Callable):
            @functools.wraps(func) #保留原函数的元信息
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)
                self.publish(event)
            return wrapper
        return decorator

    def listen_immediately(self, source: str):
        """
        添加监听器的装饰器版本\n
        该装饰器须在@publish_event之后调用（该装饰器在@publish_event上方）
        """
        def decorator(callback: Callable):
            self.add_immediate_listener(source, callback)
            return callback

        return decorator

    def listen_delayed(self, source: str,delay: int):
        """
        添加监听器的装饰器版本\n
        该装饰器须在@publish_event之后调用（该装饰器在@publish_event上方）
        """
        def decorator(callback: Callable):
            self.add_delayed_listener(source, delay, callback)
            return callback

        return decorator

    def listen_jointly(self, sources: List[str]):
        """
        添加监听器的装饰器版本\n
        该装饰器须在@publish_event之后调用（该装饰器在@publish_event上方）
        """
        def decorator(callback: Callable):
            self.add_joint_listener(sources, callback)
            return callback

        return decorator

    def listen_pattern_matcher(self, pattern: List[str]):
        """
        添加监听器的装饰器版本\n
        该装饰器须在@publish_event之后调用（该装饰器在@publish_event上方）
        """
        def decorator(callback: Callable):
            self.add_pattern_listener(pattern,callback)
            return callback

        return decorator





class JointCondition:
    def __init__(self, required_events: Set[str], callback: Callable):
        self.required = required_events
        self.occurred: Set[str] = set()
        self.callback = callback

    def reset(self):
        self.occurred = set()

    def on_event(self, event: str):
        if event in self.required and event not in self.occurred:
            self.occurred.add(event)
            if self.occurred == self.required:
                logger.info(f"EVENTBUS: event callback <func: {self.callback.__name__}> is triggered")
                self.callback()
                self.reset()  # 触发后重置


class PatternMatcher:
    def __init__(self, pattern: List[str], callback: Callable):
        self.pattern = pattern
        self.state = 0  # 当前匹配位置
        self.callback = callback

    def reset(self):
        self.state = 0

    def on_event(self, event: str):
        # 当前状态未完成匹配
        if self.state < len(self.pattern):
            # 检查事件是否匹配当前模式位置
            if self.pattern[self.state] == '*' or self.pattern[self.state] == event:
                self.state += 1
                # 完全匹配时触发
                if self.state == len(self.pattern):
                    logger.info(f"EVENTBUS: event callback <func: {self.callback.__name__}> is triggered")
                    self.callback()
                    self.reset()  # 触发后重置
            else:
                # 匹配失败时重置状态机，并尝试重新匹配当前事件
                self.reset()
                if self.pattern[0] == '*' or self.pattern[0] == event:
                    self.state = 1
                    if self.state == len(self.pattern):
                        logger.info(f"EVENTBUS: event callback <func: {self.callback.__name__}> is triggered")
                        self.callback()
                        self.reset()

"""
示例1：

if __name__ == '__main__':
    bus = EventBus()

    # 立即触发：A -> B
    bus.add_immediate_listener("A", lambda: print("B triggered"))

    # 延迟触发：A -> 等待2事件 -> C
    bus.add_delayed_listener("A", 2, lambda: print("C triggered (delayed)"))

    # 联合触发：A和B都发生 -> D
    bus.add_joint_listener(["A", "B"], lambda: print("D triggered"))

    # 模式触发：序列[A, *, B] -> E
    bus.add_pattern_listener(["A", "*", "B"], lambda: print("E triggered"))

    # 测试事件序列
    logger.debug('event A')
    bus.publish("A")  # 触发B，注册延迟C，联合记录A，模式状态1
    logger.debug('event X')
    bus.publish("X")  # 模式状态2（*匹配X）
    logger.debug('event B')
    bus.publish("B")  # 触发D（联合完成），触发E（模式完成）
"""


"""
示例2: 

if __name__ == '__main__':
    bus = EventBus()


    def publish_event_A():
        bus.publish('A')
        logger.debug('publish_event_A')

    @bus.listen_immediately('A')
    def eventB():
        bus.publish('B')
        logger.debug('eventB triggered immediately: A -> B')

    @bus.listen_delayed('A',3)
    def eventC():
        bus.publish('C')
        logger.debug('eventC triggered delay: A -> (delay) -> C')

    @bus.listen_jointly(['A','B'])
    def eventD():
        bus.publish('D')
        logger.debug('eventD triggered jointly: A+B -> D')

    @bus.listen_pattern_matcher(['A','*','D'])
    def eventE():
        bus.publish('E')
        logger.debug('eventE triggered pattern: A,*,D -> E')

    publish_event_A()
    while True:
        is_done = bus.process()
        if is_done:
            break
"""

# if __name__ == '__main__':
#     bus = EventBus()
#
#     @bus.publish_event('A')
#     def publish_event_A():
#         logger.debug('publish_event_A')
#
#     @bus.listen_immediately('A')
#     @bus.publish_event('B')
#     def eventB():
#         logger.debug('eventB triggered immediately: A -> B')
#
#     @bus.listen_delayed('A',3)
#     @bus.publish_event('C')
#     def eventC():
#         logger.debug('eventC triggered delay: A -> (delay) -> C')
#
#     @bus.listen_jointly(['A','B'])
#     @bus.publish_event('D')
#     def eventD():
#         logger.debug('eventD triggered jointly: A+B -> D')
#
#     @bus.listen_pattern_matcher(['A','*','D'])
#     @bus.publish_event('E')
#     def eventE():
#         logger.debug('eventE triggered pattern: A,*,D -> E')
#
#     publish_event_A()
#     # while True:
#     #     is_done = bus.process_one_step()
#     #     if is_done:
#     #         break
#     bus.process()


"""
示例 4: 事件风暴

if __name__ == '__main__':

    bus = EventBus()

    @bus.listen_immediately('B')
    @bus.publish_event('A')
    def publish_event_A():
        logger.debug('publish_event_A')

    @bus.listen_immediately('A')
    @bus.publish_event('B')
    def publish_event_B():
        logger.debug('publish_event_B')

    publish_event_A()
    bus.process(maxStep=1000)
    """








