"""
Testes de integração para o provedor Arcee
"""

import pytest
from arcee_cli.infrastructure.providers.arcee_provider import ArceeProvider


def test_provider_initialization():
    """Testa se o provedor é inicializado corretamente"""
    provider = ArceeProvider()
    assert provider is not None


@pytest.mark.skip(reason="Requer chave de API válida")
def test_provider_chat():
    """Testa se o chat funciona corretamente"""
    provider = ArceeProvider()
    messages = [{"role": "user", "content": "Olá!"}]
    response = provider.generate_content_chat(messages)
    assert "choices" in response
    assert len(response["choices"]) > 0
    assert "message" in response["choices"][0]
    assert "content" in response["choices"][0]["message"]
