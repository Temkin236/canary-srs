import os
from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    """
    Abstract AI model provider interface for generating reference model answers.
    Adheres strictly to Philosophical Invariant 4: Worker answers must never be sent
    to external AI providers without explicit user opt-in and consent.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider service (e.g. 'offline-synthetic', 'gemini')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the model (e.g. 'canary-synthetic-v1', 'gemini-1.5-pro')."""
        pass

    @abstractmethod
    def generate_reference(self, prompt: str) -> str:
        """Generates a reference response for the given task prompt."""
        pass


class MockAIProvider(AIProvider):
    """
    Deterministic offline synthetic provider for testing, air-gapped environments,
    and privacy-first audits without external network dependencies.
    """

    def __init__(self, model_name: str = "canary-synthetic-v1"):
        self._model_name = model_name

    @property
    def provider_name(self) -> str:
        return "offline-synthetic"

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_reference(self, prompt: str) -> str:
        clean_prompt = prompt.strip()
        # Deterministic synthetic reference based on prompt tokens
        words = clean_prompt.split()
        keywords = " ".join(words[: min(6, len(words))])
        return (
            f"Here is a comprehensive overview regarding {keywords}. "
            f"When considering this topic, multiple key dimensions should be analyzed: "
            f"structural context, standard operational methods, and verifiable empirical outcomes."
        )


class ExternalAIProvider(AIProvider):
    """
    External LLM provider with mandatory explicit consent enforcement.
    """

    def __init__(
        self,
        consent_external_ai: bool,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash",
    ):
        if not consent_external_ai:
            raise PermissionError(
                "Philosophical Invariant 4 Violation: External AI providers cannot be instantiated "
                "or queried without explicit user consent (consent_external_ai=True)."
            )

        self._model_name = model_name
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "API key missing: An API key must be provided or "
                "GEMINI_API_KEY set in the environment."
            )

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_reference(self, prompt: str) -> str:
        # In production with installed google-genai, call client.
        # Fallback to simulated response for testing without live key
        return (
            f"[External Reference - {self._model_name}] Comprehensive analysis for: {prompt[:80]}"
        )


def get_ai_provider(
    provider_type: str = "offline-synthetic",
    consent_external_ai: bool = False,
    model_name: Optional[str] = None,
) -> AIProvider:
    """
    Factory to retrieve an AIProvider instance with consent guard.
    """
    if provider_type in ("offline-synthetic", "mock"):
        return MockAIProvider(model_name=model_name or "canary-synthetic-v1")
    elif provider_type in ("gemini", "external"):
        return ExternalAIProvider(
            consent_external_ai=consent_external_ai,
            model_name=model_name or "gemini-1.5-flash",
        )
    else:
        raise ValueError(f"Unknown AI provider type: {provider_type}")
