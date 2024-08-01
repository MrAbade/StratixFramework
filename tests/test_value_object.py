import inspect
from abc import ABC
from typing import Generic, TypeVar

import pytest
from pydantic import Field, ValidationError

from stratix_framework import ValueObject


def test_value_object() -> None:
    class MyValueObject(ValueObject):
        a: str
        b: int | str = 543
        c: str = Field(examples=["aa", "bb"])
        d: str = Field(frozen=True)

        def show_value_obj(self) -> str:
            return f"{self.a} - {self.b} - {self.c}"

    fields = {"a": "a", "b": "b", "c": "c", "d": "d"}
    my_value_object = MyValueObject(**fields)

    for model_attr_name in iter(my_value_object.model_fields_set):
        with pytest.raises(ValidationError):
            setattr(my_value_object, model_attr_name, "Binho")

    assert my_value_object == my_value_object.model_copy(deep=True)
    show_value_obj_func = getattr(my_value_object, "show_value_obj", None)
    assert show_value_obj_func is not None
    assert inspect.ismethod(show_value_obj_func)
    new_fields = {"a": "a1", "b": "b1"}
    another_value_object = my_value_object.model_copy(
        update={**fields, **new_fields},
        deep=True,
    )
    assert my_value_object != another_value_object
    with pytest.raises(AssertionError):
        assert my_value_object == another_value_object


def test_abstract_value_object() -> None:
    T = TypeVar("T", bound=ValueObject)

    class MyAbstractValueObject(ValueObject, Generic[T], ABC):
        generic_attr: T

    class MyValueObject(ValueObject):
        a: str

    class AnotherValueObject(MyAbstractValueObject[MyValueObject]):
        other_attr: str

    my_value_object = MyValueObject(a="a")
    another_value_object = AnotherValueObject(generic_attr=my_value_object, other_attr="a")
    with pytest.raises(ValidationError):
        setattr(another_value_object, "generic_attr", my_value_object.model_copy(deep=True))
    generic_attr = getattr(another_value_object, "generic_attr", None)
    assert generic_attr is not None
    assert getattr(generic_attr, "a", None) is not None
