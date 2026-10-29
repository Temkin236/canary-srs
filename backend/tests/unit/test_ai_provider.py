import pytest

from app.services.ai_provider import ExternalAIProvider, MockAIProvider, get_ai_provider


def test_mock_ai_provider_runs_offline():
    provider = get_ai_provider("offline-synthetic")
    assert isinstance(provider, MockAIProvider)
    assert provider.provider_name == "offline-synthetic"
    ref = provider.generate_reference("Describe the process of cellular mitosis.")
    assert "cellular mitosis" in ref
    assert len(ref) > 20


def test_external_ai_provider_strictly_blocks_without_consent():
    with pytest.raises(PermissionError) as exc_info:
        get_ai_provider("gemini", consent_external_ai=False)
    assert "Philosophical Invariant 4 Violation" in str(exc_info.value)

    with pytest.raises(PermissionError):
        ExternalAIProvider(consent_external_ai=False)


def test_external_ai_provider_requires_api_key_when_consented(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc_info:
        get_ai_provider("gemini", consent_external_ai=True)
    assert "API key missing" in str(exc_info.value)
