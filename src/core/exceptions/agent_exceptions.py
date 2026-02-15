"""
Exceções relacionadas aos agentes de IA.

Define exceções específicas para erros na comunicação
e processamento com a API do Google Gemini.
"""

from .base_exception import RevisorTextosException


class AgentException(RevisorTextosException):
    """Exceção base para erros de agentes de IA."""

    pass


class APIException(AgentException):
    """
    Exceção para erros na comunicação com a API.

    Lançada quando há falha na comunicação com a API
    do Gemini após todas as tentativas de retry.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem, codigo="API_ERRO")


class TimeoutException(AgentException):
    """
    Exceção para timeout na requisição à API.

    Lançada quando a requisição excede o tempo limite
    configurado para resposta da API.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem, codigo="API_TIMEOUT")


class RateLimitException(AgentException):
    """
    Exceção para exceder limite de taxa da API.

    Lançada quando o número de requisições excede o
    limite configurado por minuto.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(
            mensagem, codigo="API_RATE_LIMIT"
        )


class InvalidResponseException(AgentException):
    """
    Exceção para resposta inválida da API.

    Lançada quando a resposta da API não pode ser
    parseada ou contém dados inválidos.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(
            mensagem, codigo="API_RESPOSTA_INVALIDA"
        )
