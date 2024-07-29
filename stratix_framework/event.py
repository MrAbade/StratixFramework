from abc import ABC
from datetime import datetime
from typing import Unpack, TypedDict
from uuid import UUID, uuid4

from .interfaces import BaseEvent, BaseEventBus, PublishAlgorithm
from .value_object import ValueObject
from .tools import  to_pascal_case


class DomainEvent(BaseEvent[ValueObject]):
    def __init__(self, payload: ValueObject) -> None:
        self.payload = payload

    def __new__(cls, *args, **kwargs):
        new_domain_event = super().__new__(cls)
        if not hasattr(new_domain_event, "id"):
            new_domain_event.id = uuid4()
        if not hasattr(new_domain_event, "created_at"):
            new_domain_event.created_at = datetime.now()
        return new_domain_event

    def __init_subclass__(cls, **kwargs):
        context: str = kwargs.get("context")
        context = to_pascal_case(context) if context else ""
        cls.name = f"[{context}] {cls.__name__}"
        cls.__annotations__ = {
            "id": UUID,
            "created_at": datetime,
            "name": str,
            "payload": ValueObject
        }
        try:
            return super().__init_subclass__(**kwargs)
        except TypeError:
            return super().__init_subclass__()


class PrinterPublisher(PublishAlgorithm[DomainEvent]):
    def publish(self, event: DomainEvent) -> None:
        print(event)


class InMemoryEventBus(BaseEventBus[PrinterPublisher]): ...
