"""
Deterministic offline mock adapter with basic identifier pattern screening.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Insulin Infusion Dka Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return "Mock response only. No language model, clinical validation, or guideline interpretation was performed."


class LLMFactory:
    """Creates the local mock; other providers are not implemented."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Insulin Infusion Dka Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError(
            "Requested LLM provider is not implemented; "
            "only the local deterministic mock is supported."
        )
