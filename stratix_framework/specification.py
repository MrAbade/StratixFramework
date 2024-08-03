from abc import ABC, abstractmethod
from typing import Protocol, TypeVar

from .entity import Entity
from .value_object import ValueObject

T_business_object = TypeVar("T_business_object", bound=Entity | ValueObject)


class Specification(Protocol[T_business_object]):
    @abstractmethod
    def is_satisfied_by(self, element: T_business_object) -> bool:
        ...

    def __str__(self) -> str:
        return self.__class__.__name__.replace("Specification", "")
