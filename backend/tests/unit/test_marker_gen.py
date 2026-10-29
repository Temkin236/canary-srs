from app.schemas.marker import TaskInput
from app.services.marker_gen import (
    decode_zero_width,
    encode_zero_width,
    generate_marker_manifest,
    generate_marker_token,
    prepare_task_with_marker,
    validate_manifest,
)


def test_marker_entropy_and_uniqueness():
    markers = {generate_marker_token() for _ in range(1000)}
    # All 1000 generated markers must be unique (zero collisions)
    assert len(markers) == 1000
    for m in markers:
        assert m.startswith("cnry_")
        assert len(m) >= 15


def test_zero_width_encode_decode():
    token = "cnry_3f8a9b2c"
    encoded = encode_zero_width(token)

    # Encoded string must only contain zero-width characters
    assert all(c in ("\u200b", "\u200c", "\u200d") for c in encoded)

    decoded = decode_zero_width(f"Leading text {encoded} trailing text")
    assert decoded == token


def test_prepare_task_zero_width():
    task = TaskInput(task_id="t1", prompt="Explain gravity.")
    prepared = prepare_task_with_marker(task, hiding_method="zero_width")

    assert prepared.task_id == "t1"
    assert prepared.marker.startswith("cnry_")
    assert prepared.hiding_method == "zero_width"
    assert prepared.visible_preview == "Explain gravity."
    assert "Hidden Zero-Width Sequence" in prepared.model_received_preview
    assert len(prepared.prepared_prompt) > len("Explain gravity.")


def test_prepare_task_prompt_embedded():
    task = TaskInput(task_id="t2", prompt="Summarize Hamlet.")
    prepared = prepare_task_with_marker(task, hiding_method="prompt_embedded")

    assert prepared.hiding_method == "prompt_embedded"
    assert "Canary verification note:" in prepared.prepared_prompt
    assert prepared.marker in prepared.prepared_prompt


def test_manifest_generation_and_validation():
    t1 = prepare_task_with_marker(TaskInput(task_id="t1", prompt="P1"))
    t2 = prepare_task_with_marker(TaskInput(task_id="t2", prompt="P2"))

    manifest = generate_marker_manifest([t1, t2])
    assert manifest.format_version == "1.0"
    assert len(manifest.items) == 2

    # Validate valid dict
    valid, err = validate_manifest(manifest.model_dump())
    assert valid is True
    assert err is None

    # Validate malformed dict
    invalid, err = validate_manifest({"items": [{"task_id": "only_task"}]})
    assert invalid is False
    assert "missing" in err.lower()
