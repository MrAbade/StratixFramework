import inspect
from abc import ABC, abstractmethod
from typing import ClassVar, Generic, Self, Type, TypeVar, get_args
from uuid import UUID, uuid4

from .event import InMemoryEventBus
from .interfaces import BaseEventBus, DomainException

V = TypeVar("V")


class _BaseEntityId(Generic[V], ABC):
    id: V

    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    def __eq__(self, value: object) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def __ne__(self, value: object) -> bool:
        raise NotImplementedError()

    def __repr__(self) -> V:
        return self.id

    def __str__(self) -> str:
        return str(self.id)

    def __dict__(self) -> dict[str, V]:
        return {"entity_id": self.id}


class EntityUUID(_BaseEntityId[UUID]):
    id: UUID

    def __init__(self) -> None:
        self.id = uuid4()

    def __eq__(self, value: "EntityUUID") -> bool:
        if not isinstance(value, self.__class__):
            return False
        return str(self.id) == str(value.id)

    def __ne__(self, value: object) -> bool:
        return not self == value


class CannotChangeTheEntityId(DomainException): ...


class CannotDeleteTheEntityId(DomainException): ...


class NotSupportedEventBusType(DomainException): ...


class CannotAutomaticallyPropagateEventsWitoutDefaultEventBus(DomainException): ...


class PropagateEventsParamMustBeBoolean(DomainException): ...


class PureEntityParamMustBeBoolean(DomainException): ...


class CannotDefineAnEventBusToAPureEntity(DomainException): ...


class NotSupportedEntityIdType(DomainException): ...


T = TypeVar("T", bound=_BaseEntityId)


class Entity(Generic[T], ABC):
    __orig_bases__: ClassVar[tuple[Type]]
    __type_T__: ClassVar[Type[T]]
    __entity_id__: T

    @property
    def entity_id(self) -> T:
        return self.__entity_id__.id

    @entity_id.setter
    def entity_id(self) -> None:
        raise CannotChangeTheEntityId()

    @entity_id.deleter
    def entity_id(self) -> None:
        raise CannotDeleteTheEntityId()

    def __new__(cls) -> Self:
        new_instance = super().__new__(cls)
        new_instance.__entity_id__ = new_instance.__type_T__()
        return new_instance

    def __init_subclass__(cls, *_, **kwargs) -> None:
        cls.__type_T__ = get_args(cls.__orig_bases__[0])[0]
        if not issubclass(cls.__type_T__, _BaseEntityId):
            raise NotSupportedEntityIdType()
        if (event_bus_type := kwargs.get("event_bus")) is not None:
            if not inspect.isclass(event_bus_type):
                raise NotSupportedEventBusType()
            if not issubclass(event_bus_type, BaseEventBus):
                raise NotSupportedEventBusType()
            cls.__event_bus__ = event_bus_type()
        if propagate_events := kwargs.get("propagate_events"):
            if propagate_events is not True and propagate_events is not False:
                raise PropagateEventsParamMustBeBoolean()
            if cls.__event_bus__ is None:
                raise CannotAutomaticallyPropagateEventsWitoutDefaultEventBus()
            if propagate_events:
                cls.__propagate_events__ = True
            else:
                cls.__propagate_events__ = False
        else:
            cls.__propagate_events__ = False
        if (pure_entity := kwargs.get("pure_entity")) is not None:
            if pure_entity is not True and pure_entity is not False:
                raise PureEntityParamMustBeBoolean()
            if pure_entity and (cls.__event_bus__ is not None or cls.__propagate_events__):
                raise CannotDefineAnEventBusToAPureEntity()
            if not pure_entity and cls.__event_bus__ is None:
                cls.__event__bus__ = InMemoryEventBus()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity) and not isinstance(other, self.__type_T__):
            return False
        if isinstance(other, self.__type_T__):
            return self.entity_id == other
        return self.entity_id == other.entity_id

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return not self == other
