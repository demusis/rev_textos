"""
Testes para o GeminiGateway.
"""

from unittest.mock import patch, MagicMock
from src.infrastructure.ai.gemini_gateway import GeminiGateway

def test_listar_modelos_mock():
    """Testa listar_modelos em modo mock."""
    gateway = GeminiGateway(api_key="test", modo_mock=True)
    modelos = gateway.listar_modelos()
    assert "gemini-2.0-flash (mock)" in modelos

@patch("src.infrastructure.ai.gemini_gateway.genai")
def test_listar_modelos_api(mock_genai):
    """Testa listar_modelos com chamada de API simulada."""
    # Setup mock
    m1 = MagicMock()
    m1.name = "models/gemini-pro"
    m1.supported_generation_methods = ["generateContent"]
    
    m2 = MagicMock()
    m2.name = "models/gemini-vision"
    m2.supported_generation_methods = ["otherMethod"]
    
    mock_genai.list_models.return_value = [m1, m2]
    
    gateway = GeminiGateway(api_key="test", modo_mock=False)
    modelos = gateway.listar_modelos()
    
    # Deve retornar apenas o que suporta generateContent e sem prefixo
    assert "gemini-pro" in modelos
    assert "gemini-vision" not in modelos
