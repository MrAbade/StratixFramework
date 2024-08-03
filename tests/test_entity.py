from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4

import pytest

from stratix_framework import Entity, IdUUID, IdString, IdInt, IdBytes, ValueObject, Specification
from stratix_framework.entity import CannotChangeTheEntityId, CannotDeleteTheEntityId
from stratix_framework.event import DomainEvent


def test_entity_uuid() -> None:
    class ExampleEntity(Entity[IdUUID]): ...

    entity = ExampleEntity()

    assert isinstance(entity.entity_id, UUID)
    assert isinstance(entity.__entity_id__, IdUUID)

    with pytest.raises(CannotChangeTheEntityId):
        entity.entity_id = "Some Value"
    with pytest.raises(CannotChangeTheEntityId):
        entity.entity_id = uuid4

    with pytest.raises(CannotDeleteTheEntityId):
        del entity.entity_id

    uuid_id = entity.__entity_id__
    assert entity == uuid_id
    assert entity == uuid_id.id

    pre_existing_id_1 = uuid4()
    pre_existing_id_2 = uuid4()
    assert pre_existing_id_1 != pre_existing_id_2

    class ExampleEntity2(Entity[IdUUID], with_fixed_id=pre_existing_id_1): ...

    class ExampleEntity3(Entity[IdUUID], with_fixed_id=pre_existing_id_2): ...

    entity2 = ExampleEntity2()
    entity3 = ExampleEntity3()

    assert entity2 != entity3

    assert entity2 == pre_existing_id_1
    assert entity3 == pre_existing_id_2

    class ExampleEntity4(Entity[IdUUID], with_fixed_id=pre_existing_id_1): ...

    entity4 = ExampleEntity4()
    assert entity4 == pre_existing_id_1
    assert entity4 == entity2
    assert entity4 != entity3


def test_entity_string() -> None:
    class ExampleEntity(Entity[IdString]): ...

    entity = ExampleEntity()

    assert isinstance(entity.entity_id, str)
    assert isinstance(entity.__entity_id__, IdString)

    with pytest.raises(CannotChangeTheEntityId):
        entity.entity_id = "Some Value"
    with pytest.raises(CannotChangeTheEntityId):
        entity.entity_id = str

    with pytest.raises(CannotDeleteTheEntityId):
        del entity.entity_id

    string_id = entity.__entity_id__
    assert entity == string_id
    assert entity == string_id.id

    pre_existing_id_1 = str("pre_existing_id_1")
    pre_existing_id_2 = str("pre_existing_id_2")
    assert pre_existing_id_1 != pre_existing_id_2

    class ExampleEntity2(Entity[IdString], with_fixed_id=pre_existing_id_1): ...

    class ExampleEntity3(Entity[IdString], with_fixed_id=pre_existing_id_2): ...

    entity2 = ExampleEntity2()
    entity3 = ExampleEntity3()

    assert entity2 != entity3

    assert entity2 == pre_existing_id_1
    assert entity3 == pre_existing_id_2

    class ExampleEntity4(Entity[IdString], with_fixed_id=pre_existing_id_1): ...

    entity4 = ExampleEntity4()
    assert entity4 == pre_existing_id_1
    assert entity4 == entity2
    assert entity4 != entity3


def test_entity_int() -> None:
    class ExampleEntity(Entity[IdInt]): ...

    entity = ExampleEntity()

    assert isinstance(entity.entity_id, int)
    assert isinstance(entity.__entity_id__, IdInt)

    with pytest.raises(CannotChangeTheEntityId):
        entity.entity_id = 123
    with pytest.raises(CannotChangeTheEntityId):
        entity.entity_id = int

    with pytest.raises(CannotDeleteTheEntityId):
        del entity.entity_id

    int_id = entity.__entity_id__
    assert entity == int_id
    assert entity == int_id.id

    pre_existing_id_1 = 123
    pre_existing_id_2 = 456
    assert pre_existing_id_1 != pre_existing_id_2

    class ExampleEntity2(Entity[IdInt], with_fixed_id=pre_existing_id_1): ...

    class ExampleEntity3(Entity[IdInt], with_fixed_id=pre_existing_id_2): ...

    entity2 = ExampleEntity2()
    entity3 = ExampleEntity3()

    assert entity2 != entity3
    assert entity2 == pre_existing_id_1
    assert entity3 == pre_existing_id_2

    class ExampleEntity4(Entity[IdInt], with_fixed_id=pre_existing_id_1): ...

    entity4 = ExampleEntity4()
    assert entity4 == pre_existing_id_1
    assert entity4 == entity2
    assert entity4 != entity3


def test_entity_bytes() -> None:
    class ExampleEntity(Entity[IdBytes]): ...

    entity = ExampleEntity()

    assert isinstance(entity.entity_id, bytes)
    assert isinstance(entity.__entity_id__, IdBytes)

    with pytest.raises(CannotChangeTheEntityId):
        entity.entity_id = b"Some Value"
    with pytest.raises(CannotChangeTheEntityId):
        entity.entity_id = bytes

    with pytest.raises(CannotDeleteTheEntityId):
        del entity.entity_id

    bytes_id = entity.__entity_id__
    assert entity == bytes_id
    assert entity == bytes_id.id

    pre_existing_id_1 = b"pre_existing_id_1"
    pre_existing_id_2 = b"pre_existing_id_2"
    assert pre_existing_id_1 != pre_existing_id_2

    class ExampleEntity2(Entity[IdBytes], with_fixed_id=pre_existing_id_1): ...

    class ExampleEntity3(Entity[IdBytes], with_fixed_id=pre_existing_id_2): ...

    entity2 = ExampleEntity2()
    entity3 = ExampleEntity3()

    assert entity2 != entity3

    assert entity2 == pre_existing_id_1
    assert entity3 == pre_existing_id_2

    class ExampleEntity4(Entity[IdBytes], with_fixed_id=pre_existing_id_1): ...

    entity4 = ExampleEntity4()
    assert entity4 == pre_existing_id_1
    assert entity4 == entity2
    assert entity4 != entity3


def test_entity_hashing() -> None:
    class ExampleEntityUUID(Entity[IdUUID]):
        pass

    class ExampleEntityInt(Entity[IdInt]):
        pass

    class ExampleEntityStr(Entity[IdString]):
        pass

    uuid_entity = ExampleEntityUUID()
    int_entity = ExampleEntityInt()
    str_entity = ExampleEntityStr()

    assert hash(uuid_entity) != hash(int_entity)
    assert hash(uuid_entity) != hash(str_entity)
    assert hash(int_entity) != hash(str_entity)

    entities_set = {uuid_entity, int_entity, str_entity}

    assert len(entities_set) == 3
    assert uuid_entity in entities_set
    assert int_entity in entities_set
    assert str_entity in entities_set

    pre_existing_uuid = uuid4()
    pre_existing_int = 12345
    pre_existing_str = "pre_existing"

    class ExampleEntityUUIDWithId(Entity[IdUUID], with_fixed_id=pre_existing_uuid):
        pass

    class ExampleEntityIntWithId(Entity[IdInt], with_fixed_id=pre_existing_int):
        pass

    class ExampleEntityStrWithId(Entity[IdString], with_fixed_id=pre_existing_str):
        pass

    uuid_entity_with_id = ExampleEntityUUIDWithId()
    int_entity_with_id = ExampleEntityIntWithId()
    str_entity_with_id = ExampleEntityStrWithId()

    assert hash(uuid_entity_with_id) == hash(pre_existing_uuid)
    assert hash(int_entity_with_id) == hash(pre_existing_int)
    assert hash(str_entity_with_id) == hash(pre_existing_str)

    entities_set_with_ids = {uuid_entity_with_id, int_entity_with_id, str_entity_with_id}

    assert len(entities_set_with_ids) == 3
    assert uuid_entity_with_id in entities_set_with_ids
    assert int_entity_with_id in entities_set_with_ids
    assert str_entity_with_id in entities_set_with_ids


def test_entity_attributes_and_methods() -> None:
    class Address(ValueObject):
        street: str
        city: str
        state: str
        postal_code: str

    class Client(Entity[IdUUID]):
        name: str
        address: Address

        def __init__(self, name: str, address: Address) -> None:
            super().__init__()
            self.name = name
            self.address = address

    class ServiceProvider(Entity[IdUUID]):
        name: str
        address: Address
        available: bool

        def __init__(self, name: str, address: Address, available: bool) -> None:
            super().__init__()
            self.name = name
            self.address = address
            self.available = available

        def toggle_availability(self) -> None:
            self.available = not self.available

    class ClothingItem(Entity[IdUUID]):
        description: str
        client: Client

        def __init__(self, description: str, client: Client) -> None:
            super().__init__()
            self.description = description
            self.client = client

    class PickupRequest(Entity[IdUUID]):
        clothing_items: list[ClothingItem]
        client: Client
        pickup_date: datetime
        assigned_courier: str | None = None

        def __init__(self, clothing_items: list[ClothingItem], client: Client, pickup_date: datetime) -> None:
            super().__init__()
            self.clothing_items = clothing_items
            self.client = client
            self.pickup_date = pickup_date

        def assign_courier(self, courier_name: str) -> None:
            self.assigned_courier = courier_name

        def is_within_pickup_window(self, current_date: datetime, window_days: int) -> bool:
            return self.pickup_date <= current_date <= (self.pickup_date + timedelta(days=window_days))

    class DeliveryRequest(Entity[IdUUID]):
        pickup_request: PickupRequest
        service_provider: ServiceProvider
        delivery_date: datetime
        assigned_courier: str | None = None

        def __init__(
            self, pickup_request: PickupRequest, service_provider: ServiceProvider, delivery_date: datetime
        ) -> None:
            super().__init__()
            self.pickup_request = pickup_request
            self.service_provider = service_provider
            self.delivery_date = delivery_date

        def assign_courier(self, courier_name: str) -> None:
            self.assigned_courier = courier_name

        def is_within_delivery_window(self, current_date: datetime, window_days: int) -> bool:
            return self.delivery_date <= current_date <= (self.delivery_date + timedelta(days=window_days))

    class ReturnRequest(Entity[IdUUID]):
        delivery_request: DeliveryRequest
        return_date: datetime
        assigned_courier: str | None = None

        def __init__(self, delivery_request: DeliveryRequest, return_date: datetime) -> None:
            super().__init__()
            self.delivery_request = delivery_request
            self.return_date = return_date

        def assign_courier(self, courier_name: str) -> None:
            self.assigned_courier = courier_name

        def is_within_return_window(self, current_date: datetime, window_days: int) -> bool:
            return self.return_date <= current_date <= (self.return_date + timedelta(days=window_days))

    address1 = Address(street="123 Main St", city="Springfield", state="IL", postal_code="62701")
    address2 = Address(street="456 Elm St", city="Springfield", state="IL", postal_code="62702")

    client = Client(name="John Doe", address=address1)
    service_provider = ServiceProvider(name="Laundry Service", address=address2, available=True)

    clothing_item = ClothingItem(description="Shirt", client=client)

    pickup_request = PickupRequest(clothing_items=[clothing_item], client=client, pickup_date=datetime(2024, 8, 3))
    assert pickup_request.client.name == "John Doe"
    assert pickup_request.clothing_items[0].description == "Shirt"
    assert pickup_request.is_within_pickup_window(datetime(2024, 8, 4), 1) is True
    assert pickup_request.is_within_pickup_window(datetime(2024, 8, 6), 1) is False

    delivery_request = DeliveryRequest(
        pickup_request=pickup_request,
        service_provider=service_provider,
        delivery_date=datetime(2024, 8, 4),
    )
    assert delivery_request.service_provider.name == "Laundry Service"
    assert delivery_request.pickup_request.client.name == "John Doe"
    assert delivery_request.is_within_delivery_window(datetime(2024, 8, 5), 1) is True
    assert delivery_request.is_within_delivery_window(datetime(2024, 8, 7), 1) is False

    return_request = ReturnRequest(delivery_request=delivery_request, return_date=datetime(2024, 8, 5))
    assert return_request.delivery_request.service_provider.name == "Laundry Service"
    assert return_request.delivery_request.pickup_request.client.name == "John Doe"
    assert return_request.is_within_return_window(datetime(2024, 8, 6), 1) is True
    assert return_request.is_within_return_window(datetime(2024, 8, 8), 1) is False

    pickup_request.assign_courier("Courier A")
    delivery_request.assign_courier("Courier B")
    return_request.assign_courier("Courier C")

    assert pickup_request.assigned_courier == "Courier A"
    assert delivery_request.assigned_courier == "Courier B"
    assert return_request.assigned_courier == "Courier C"

    assert service_provider.available is True
    service_provider.toggle_availability()
    assert service_provider.available is False
    service_provider.toggle_availability()
    assert service_provider.available is True


def test_entity_event() -> None:
    class PartyRole(str, Enum):
        PLAINTIFF = "Reclamante"
        DEFENDANT = "Reclamado"

    class PartyStatus(str, Enum):
        ACTIVE = "Active"
        INACTIVE = "Inactive"
        COMPLETED = "Completed"

    class CaseStatusUpdated(Event):
        def __init__(self, case_id: UUID, old_status: str, new_status: str, timestamp: datetime) -> None:
            super().__init__(event_id=uuid4(), case_id=case_id, event_type="CaseStatusUpdated", timestamp=timestamp,
                             details=f"From {old_status} to {new_status}")

    class CasePartyAdded(Event):
        def __init__(self, case_id: UUID, party_id: UUID, role: str, timestamp: datetime) -> None:
            super().__init__(event_id=uuid4(), case_id=case_id, event_type="CasePartyAdded", timestamp=timestamp,
                             details=f"Party ID: {party_id}, Role: {role}")

    class CasePartyRemoved(Event):
        def __init__(self, case_id: UUID, party_id: UUID, timestamp: datetime) -> None:
            super().__init__(event_id=uuid4(), case_id=case_id, event_type="CasePartyRemoved", timestamp=timestamp,
                             details=f"Party ID: {party_id}")

    class PartyStatusChanged(DomainEvent):
        def __init__(self, party_id: UUID, process_id: UUID, old_status: PartyStatus, new_status: PartyStatus,
                     timestamp: datetime) -> None:
            self.party_id = party_id
            self.process_id = process_id
            self.old_status = old_status
            self.new_status = new_status
            self.timestamp = timestamp

    class SentencaProcessed:
        def __init__(self, event_id: UUID, case_id: UUID, timestamp: datetime) -> None:
            self.event_id = event_id
            self.case_id = case_id
            self.timestamp = timestamp

    class PeticaoProcessed:
        def __init__(self, event_id: UUID, case_id: UUID, timestamp: datetime) -> None:
            self.event_id = event_id
            self.case_id = case_id
            self.timestamp = timestamp

    class DespachoProcessed:
        def __init__(self, event_id: UUID, case_id: UUID, timestamp: datetime) -> None:
            self.event_id = event_id
            self.case_id = case_id
            self.timestamp = timestamp

    class AudienciaProcessed:
        def __init__(self, event_id: UUID, case_id: UUID, timestamp: datetime) -> None:
            self.event_id = event_id
            self.case_id = case_id
            self.timestamp = timestamp

    class CaseStatusUpdated:
        def __init__(self, case_id: UUID, old_status: str, new_status: str, timestamp: datetime) -> None:
            self.case_id = case_id
            self.old_status = old_status
            self.new_status = new_status
            self.timestamp = timestamp

    class PetitionSpecification(Specification):
        def is_satisfied_by(self, doc: "Document") -> bool:
            return "Petição Inicial" in doc.content

    class ContestationSpecification(Specification):
        def is_satisfied_by(self, doc: "Document") -> bool:
            return "Contestação" in doc.content

    class ImpugnationSpecification(Specification):
        def is_satisfied_by(self, doc: "Document") -> bool:
            return "Impugnação" in doc.content

    class ExecutionSpecification(Specification):
        def is_satisfied_by(self, doc: "Document") -> bool:
            return "Execução" in doc.content

    class Party(Entity[IdUUID]):
        def __init__(self, name: str, role: PartyRole, status: PartyStatus, process_id: str) -> None:
            super().__init__()
            self.name = name
            self.role = role
            self.status = status
            self.process_id = process_id

        def is_plaintiff(self) -> bool:
            return self.role == PartyRole.PLAINTIFF

        def is_defendant(self) -> bool:
            return self.role == PartyRole.DEFENDANT

        def update_status(self, new_status: PartyStatus) -> None:
            if new_status not in PartyStatus:
                raise ValueError(f"Invalid status: {new_status}.")
            old_status = self.status
            self.status = new_status
            self.event_bus.register(
                PartyStatusChanged(self.party_id, self.process_id, old_status, new_status, datetime.now())
            )

        def __repr__(self) -> str:
            return (
                f"Party(ID: {self.party_id}, Name: {self.name}, Role: {self.role}, "
                f"Process ID: {self.process_id}, Status: {self.status})"
            )

    class Case(Entity[IdUUID]):
        def __init__(self, case_number: str, parties: list[Party], status: str, last_updated: datetime) -> None:
            super().__init__()
            self.case_number = case_number
            self.parties = parties
            self.status = status
            self.last_updated = last_updated

        def update_status(self, new_status: str) -> None:
            old_status = self.status
            self.status = new_status
            self.last_updated = datetime.now()
            self.event_bus.register(CaseStatusUpdated(self.entity_id, old_status, new_status, self.last_updated))

        def add_party(self, party: "Party") -> None:
            if any(party.party_id == p.party_id for p in self.parties):
                raise ValueError("Party already exists in this case.")
            self.parties.append(party)
            self.event_bus.register(CasePartyAdded(self.entity_id, party.entity_id, party.role, datetime.now()))

        def remove_party(self, party: "Party") -> None:
            self.parties = [p for p in self.parties if p.party_id != party.party_id]
            self.event_bus.register(CasePartyRemoved(self.entity_id, party.entity_id, datetime.now()))

    class Document(Entity[IdUUID]):
        processed_at: datetime

        def __init__(self, case_id: UUID, document_type: str, content: str, status: str) -> None:
            super().__init__()
            self.case_id = case_id
            self.document_type = document_type
            self.content = content
            self.status = status

        def process(self) -> None:
            if self.status != "Not Processed":
                raise ValueError("Document has already been processed.")
            self.status = "Processing"
            self.event_bus.register(
                DocumentProcessingError(self.document_id, self.case_id, "Processing started", datetime.now())
            )
            self.status = "Processed"
            self.processed_at = datetime.now()
            self.event_bus.register(DocumentProcessed(self.document_id, self.case_id, self.processed_at))

        def change_document_type(self, new_type: str) -> None:
            old_type = self.document_type
            self.document_type = new_type
            self.event_bus.register(
                DocumentTypeChanged(self.document_id, self.case_id, old_type, new_type, datetime.now())
            )

        def review(self, reviewed_by: UUID) -> None:
            self.event_bus.register(DocumentReviewed(self.document_id, self.case_id, reviewed_by, datetime.now()))

        class Event(Entity[IdUUID]):
            event_type: str

            def __init__(self, case: Case, document: "Document", timestamp: datetime, details: str) -> None:
                super().__init__()
                self.case = case
                self.timestamp = timestamp
                self.document = document
                self.details = details

                self.validate_event()

            def validate_event(self) -> None:
                if self.event_type not in ["Sentença", "Petição", "Despacho", "Audiência"]:
                    raise ValueError(f"Invalid event type: {self.event_type}.")
                if self.document_id is not None:
                    if not self.validate_document():
                        raise ValueError("Associated document is not valid.")

            def validate_document(self) -> bool:
                specifications: list[Specification] = [
                    PetitionSpecification(),
                    ContestationSpecification(),
                    ImpugnationSpecification(),
                    ExecutionSpecification(),
                ]
                try:
                    document_type = next(str(spec) for spec in specifications if spec.is_satisfied_by(self.document))
                    self.event_type = document_type
                    self.event_bus.register(DocumentValidated(self.document.entity_id, document_type, datetime.now()))
                except StopIteration:
                    self.event_bus.register(DocumentValidationFailed(self.document.entity_id, datetime.now()))

            def process_event(self) -> None:
                if self.event_type == "Sentença":
                    self.handle_sentenca_event()
                elif self.event_type == "Petição":
                    self.handle_peticao_event()
                elif self.event_type == "Despacho":
                    self.handle_despacho_event()
                elif self.event_type == "Audiência":
                    self.handle_audiencia_event()

            def handle_sentenca_event(self) -> None:
                self.event_bus.register(SentencaProcessed(self.event_id, self.case_id, datetime.now()))
                self.event_bus.register(CaseStatusUpdated(self.case_id, "Sentença", datetime.now()))

            def handle_peticao_event(self) -> None:
                self.event_bus.register(PeticaoProcessed(self.event_id, self.case_id, datetime.now()))
                self.event_bus.register(CaseStatusUpdated(self.case_id, "Petição", datetime.now()))

            def handle_despacho_event(self) -> None:
                self.event_bus.register(DespachoProcessed(self.event_id, self.case_id, datetime.now()))
                self.event_bus.register(CaseStatusUpdated(self.case_id, "Despacho", datetime.now()))

            def handle_audiencia_event(self) -> None:
                self.event_bus.register(AudienciaProcessed(self.event_id, self.case_id, datetime.now()))
                self.event_bus.register(CaseStatusUpdated(self.case_id, "Audiência", datetime.now()))

            def __repr__(self) -> str:
                return (
                    f"Event(ID: {self.entity_id}, Case ID: {self.case_id}, Document ID: {self.document_id}, "
                    f"Type: {self.event_type}, Timestamp: {self.timestamp}, Details: {self.details})"
                )