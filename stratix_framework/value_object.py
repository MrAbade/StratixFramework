import inspect
from abc import ABC

from pydantic import BaseModel, ConfigDict, Field
from pydantic.fields import FieldInfo


class BaseValueObject(BaseModel, ABC):
    model_config = ConfigDict(
        arbitrary_types_allowed=False,
        extra="forbid",
        use_enum_values=True,
    )

    def __init_subclass__(cls, **kwargs):
        return cls.__transform_into_object_value__(**kwargs)

    @classmethod
    def __transform_into_object_value__(cls, **kwargs):
        for attr_name in cls.__annotations__.keys():
            attr_value = getattr(cls, attr_name, None)
            if attr_value is None:
                setattr(cls, attr_name, Field(frozen=True))
            elif isinstance(attr_value, FieldInfo):
                field_info_attrs = attr_value._attributes_set
                if "frozen" not in field_info_attrs:
                    setattr(cls, attr_name, Field(**field_info_attrs, frozen=True))
            else:
                setattr(cls, attr_name, Field(attr_value, frozen=True))
        try:
            return super().__init_subclass__(**kwargs)
        except TypeError:
            return super().__init_subclass__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObject):
            return False
        self_attributes = vars(self)
        other_attributes = vars(other)
        return self_attributes == other_attributes

    def __ne__(self, other: object) -> bool:
        return not self == other


class ValueObject(BaseValueObject, ABC):
    pass
