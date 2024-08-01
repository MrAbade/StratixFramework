import pytest


def test_event() -> None:
    from stratix_framework.event import DomainEvent
    from stratix_framework import ValueObject

    class VideoHasFinishedProcessing(DomainEvent, context="VideoProcessor"): ...

    class VideoHasFinishedProcessingV2(DomainEvent, context="VideoProcessor"): ...

    class VideoPayload(ValueObject):
        video_id: str

    video_has_finished_processing = VideoHasFinishedProcessing(
        payload=VideoPayload(video_id="123"),
    )
    video_has_finished_processing_v2 = VideoHasFinishedProcessingV2(
        payload=VideoPayload(video_id="345"),
    )
    assert video_has_finished_processing.name == "[VideoProcessor] VideoHasFinishedProcessing"
    assert video_has_finished_processing.payload.video_id == "123"
    assert video_has_finished_processing == video_has_finished_processing
    assert video_has_finished_processing != "VideoHasFinishedProcessing"
    assert video_has_finished_processing < video_has_finished_processing_v2
    assert str(video_has_finished_processing) == "[VideoProcessor] VideoHasFinishedProcessing"
    assert repr(video_has_finished_processing) == "Event <[VideoProcessor] VideoHasFinishedProcessing> created at " + str(video_has_finished_processing.created_at)
    assert video_has_finished_processing.__dict__() == {
        "id": video_has_finished_processing.id,
        "created_at": video_has_finished_processing.created_at,
        "name": video_has_finished_processing.name,
        "payload": video_has_finished_processing.payload,
    }
    with pytest.raises(TypeError):
        video_has_finished_processing.__gt__("VideoHasFinishedProcessing")
    with pytest.raises(TypeError):
        video_has_finished_processing.__lt__("VideoHasFinishedProcessing")
    with pytest.raises(TypeError):
        video_has_finished_processing.__eq__(1)
    with pytest.raises(TypeError):
        video_has_finished_processing.__ne__(1)
