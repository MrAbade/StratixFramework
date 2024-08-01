import inspect
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, ClassVar, Generic, Protocol, Self, Type, TypeVar, get_args, runtime_checkable
from uuid import UUID, uuid4

from pydantic import Field

from .value_object import ValueObject

T = TypeVar("T", bound=ValueObject)


class BaseEvent(Generic[T]):
    id: UUID
    created_at: datetime
    name: str
    payload: T | None

    def __gt__(self, obj: object) -> bool:
        if not isinstance(obj, BaseEvent):
            raise TypeError(f"Cannot compare an Event with {obj.__class__.__name__}")
        return self.created_at > obj.created_at

    def __lt__(self, obj: object) -> bool:
        if not isinstance(obj, BaseEvent):
            raise TypeError(f"Cannot compare an Event with {obj.__class__.__name__}")
        return self.created_at < obj.created_at

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, BaseEvent) and not isinstance(obj, str):
            raise TypeError(f"Cannot compare an Event with {obj.__class__.__name__}")
        if isinstance(obj, BaseEvent):
            return self.name == obj.name
        return self.name == obj

    def __ne__(self, other) -> bool:
        return not self == other

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Event <{self.name}> created at {self.created_at}"

    def __dict__(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "name": self.name,
            "payload": self.payload,
        }


T_Event = TypeVar("T_Event", bound=BaseEvent)


@runtime_checkable
class PublishAlgorithm(Protocol[T_Event]):
    @abstractmethod
    def publish(self, event: T_Event) -> None: ...


class _BaseException(RuntimeError):
    def __init__(self) -> None:
        self.msg = self.__class__.__name__


class DomainException(_BaseException): ...


class ApplicationException(_BaseException): ...


class NotSupportedAlgorithmForPublishing(ApplicationException): ...


class NotSupportedLogType(ApplicationException): ...


class EventNotFoundWhenTryingToPublishSpecificEvent(ApplicationException): ...


T_PublishAlgorithm = TypeVar("T_PublishAlgorithm", bound=PublishAlgorithm)


class BaseEventBus(Generic[T_PublishAlgorithm]):
    __orig_bases__: ClassVar[tuple[Type]]
    __log_class__: ClassVar[Type[Any] | None] = None
    __publish_algorithm_type__: ClassVar[Type[T_PublishAlgorithm] | None] = None
    __publish_algorithm__: T_PublishAlgorithm | None
    __events__: list[BaseEvent] | None = None

    def __new__(cls) -> "BaseEventBus":
        new_instance = super().__new__()
        if cls.__publish_algorithm_type__ is not None:
            new_instance.__publish_algorithm__ = cls.__publish_algorithm_type__()
        return new_instance

    def __init_subclass__(cls, *_, **kwargs) -> None:
        publish_algorithm_type = get_args(cls.__orig_bases__[0])[0]
        if not issubclass(publish_algorithm_type, PublishAlgorithm):
            raise NotSupportedAlgorithmForPublishing()
        cls.__publish_algorithm_type__ = publish_algorithm_type
        if (log_type := kwargs.get("log")) is not None:
            if not inspect.isclass(log_type):
                raise NotSupportedLogType()
            cls.__log_class__ = log_type
        return super().__init_subclass__()

    @abstractmethod
    def publish(self) -> None:
        for event in self.__events__:
            self.__publish_algorithm__.publish(event)
            # TODO: add logging

    @abstractmethod
    def publish_only(self, event_name: str) -> None:
        found_event = next((event for event in self.__events__ if event == event_name), None)
        if not found_event:
            raise EventNotFoundWhenTryingToPublishSpecificEvent()
        self.__publish_algorithm__.publish(found_event)
        # TODO: add logging

    @abstractmethod
    def register(self, event: BaseEvent) -> None:
        self.__events__.append(event)

    @abstractmethod
    def has_event(self, event_name: str) -> bool:
        return any(event == event_name for event in self.__events__)

    @abstractmethod
    def count(self) -> int:
        return len(self.__events__)

    @abstractmethod
    def __len__(self) -> int:
        return self.count()

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __repr__(self) -> str: ...
