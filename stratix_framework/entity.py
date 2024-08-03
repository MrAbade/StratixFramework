import inspect
import random
from abc import ABC, abstractmethod
from typing import ClassVar, Generic, Self, Type, TypeVar, get_args, Any
from uuid import UUID, uuid4, uuid5, NAMESPACE_DNS

from .event import InMemoryEventBus
from .interfaces import BaseEventBus, DomainException

V = TypeVar("V")


class _BaseEntityId(Generic[V], ABC):
    __type_id__ = V

    id: V

    @abstractmethod
    def __init__(self, id_value: V | None = None) -> None: ...

    @abstractmethod
    def __eq__(self, value: object) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def __ne__(self, value: object) -> bool:
        raise NotImplementedError()

    def __hash__(self):
        raise NotImplementedError()

    def __repr__(self) -> V:
        return str(self.id)

    def __str__(self) -> str:
        return str(self.id)

    def __dict__(self) -> dict[str, V]:
        return {"entity_id": self.id}


class IdUUID(_BaseEntityId[UUID]):
    id: UUID

    def __init__(self, id_value: UUID | None = None) -> None:
        self.id = id_value if id_value is not None else uuid4()

    def __eq__(self, value: "IdUUID") -> bool:
        if not isinstance(value, self.__class__) and not isinstance(value, UUID):
            return False
        if isinstance(value, UUID):
            return str(self.id) == str(value)
        return str(self.id) == str(value.id)

    def __ne__(self, value: object) -> bool:
        return not self == value

    def __hash__(self):
        return hash(self.id)


class IdString(_BaseEntityId[str]):
    id: str

    def __init__(self, id_value: str | None = None) -> None:
        self.id = id_value if id_value is not None else str(uuid4())

    def __eq__(self, value: "IdString") -> bool:
        if not isinstance(value, self.__class__) and not isinstance(value, str):
            return False
        if isinstance(value, str):
            return self.id == value
        return self.id == value.id

    def __ne__(self, value: object) -> bool:
        return not self == value

    def __hash__(self):
        return hash(uuid5(NAMESPACE_DNS, self.id))


class IdInt(_BaseEntityId[int]):
    id: int

    def __init__(self, id_value: int | None = None) -> None:
        self.id = id_value if id_value is not None else self.__random_id()

    def __eq__(self, value: "IdInt") -> bool:
        if not isinstance(value, self.__class__) and not isinstance(value, int):
            return False
        if isinstance(value, int):
            return self.id == value
        return self.id == value.id

    def __ne__(self, value: object) -> bool:
        return not self == value

    def __hash__(self):
        return hash(uuid5(NAMESPACE_DNS, str(self.id)))

    @staticmethod
    def __random_id() -> int:
        num_digits = random.randint(5, 10)
        min_value = 10 ** (num_digits - 1)
        max_value = 10 ** num_digits - 1

        return random.randint(min_value, max_value)


class IdBytes(_BaseEntityId[bytes]):
    id: bytes

    def __init__(self, id_value: bytes | None = None) -> None:
        self.id = id_value if id_value is not None else uuid4().bytes

    def __eq__(self, value: "IdBytes") -> bool:
        if not isinstance(value, self.__class__) and not isinstance(value, bytes):
            return False
        if isinstance(value, bytes):
            return self.id == value
        return self.id == value.id

    def __ne__(self, value: object) -> bool:
        return not self == value

    def __hash__(self):
        return hash(uuid5(NAMESPACE_DNS, self.id))


class CannotChangeTheEntityId(DomainException): ...


class CannotDeleteTheEntityId(DomainException): ...


class NotSupportedEventBusType(DomainException): ...


class CannotAutomaticallyPropagateEventsWitoutDefaultEventBus(DomainException): ...


class PropagateEventsParamMustBeBoolean(DomainException): ...


class PureEntityParamMustBeBoolean(DomainException): ...


class CannotDefineAnEventBusToAPureEntity(DomainException): ...


class NotSupportedEntityIdType(DomainException): ...


class NotSupportedEntityIdValue(DomainException): ...


T = TypeVar("T", bound=_BaseEntityId)


class Entity(Generic[T], ABC):
    __orig_bases__: ClassVar[tuple[Type]]
    __type_T__: ClassVar[T.__bound__]
    __entity_id__: T
    __entity_id_value__: T.__bound__.__type_id__ = None
    __event_bus__: BaseEventBus | None = None

    @property
    def entity_id(self) -> T:
        return self.__entity_id__.id

    @entity_id.setter
    def entity_id(self, _: Any) -> None:
        raise CannotChangeTheEntityId()

    @entity_id.deleter
    def entity_id(self) -> None:
        raise CannotDeleteTheEntityId()

    @property
    def event_bus(self):
        return self.__event_bus__

    def __new__(cls, *args, **kwargs) -> "Entity":
        new_instance = super().__new__(cls)
        entity_id_value = new_instance.__entity_id_value__
        if entity_id_value is not None:
            new_instance.__entity_id__ = new_instance.__type_T__(entity_id_value)
        else:
            new_instance.__entity_id__ = new_instance.__type_T__()

        return new_instance

    def __init_subclass__(cls, *_, **kwargs) -> None:
        cls.__type_T__ = get_args(cls.__orig_bases__[0])[0]
        if not issubclass(cls.__type_T__, _BaseEntityId):
            raise NotSupportedEntityIdType()
        if (id_value := kwargs.get("with_fixed_id")) is not None:
            id_value_type = cls.__type_T__.__annotations__.get("id")
            if not isinstance(id_value, id_value_type):
                raise NotSupportedEntityIdValue()
            cls.__entity_id_value__ = id_value
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
        if (
            not isinstance(other, Entity)
            and not isinstance(other, self.__type_T__)
            and not isinstance(other, type(self.__entity_id__.id))
        ):
            return False
        if isinstance(other, Entity):
            return self.entity_id == other.entity_id
        return self.entity_id == other

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return not self == other

    def __hash__(self) -> int:
        return hash(self.entity_id)
