import pytest

from stratix_framework import Entity, EntityUUID


def test_entity() -> None:
    class ExampleEntity(Entity[EntityUUID]): ...

    entity = ExampleEntity()
    print(entity.entity_id)
