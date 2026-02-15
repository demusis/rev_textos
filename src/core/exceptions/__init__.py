"""Exceções customizadas do sistema de revisão de textos."""

from .base_exception import RevisorTextosException
from .texto_exceptions import (
    TextoException,
    TextoInvalidoException,
    TextoNaoEncontradoException,
    SecaoNaoEncontradaException,
    SecaoDuplicadaException,
)
from .agent_exceptions import (
    AgentException,
    APIException,
    TimeoutException,
    RateLimitException,
    InvalidResponseException,
)
from .pdf_exceptions import (
    PDFException,
    PDFInvalidoException,
    PDFProtegidoException,
    ExtracaoException,
)

__all__ = [
    "RevisorTextosException",
    "TextoException",
    "TextoInvalidoException",
    "TextoNaoEncontradoException",
    "SecaoNaoEncontradaException",
    "SecaoDuplicadaException",
    "AgentException",
    "APIException",
    "TimeoutException",
    "RateLimitException",
    "InvalidResponseException",
    "PDFException",
    "PDFInvalidoException",
    "PDFProtegidoException",
    "ExtracaoException",
]
