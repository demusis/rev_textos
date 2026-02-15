"""
Interface do sistema de logging.

Define o contrato para logging estruturado
utilizado por todos os componentes.
"""

from abc import ABC, abstractmethod
from typing import Any


class ILogger(ABC):
    """
    Interface para sistema de logging.

    Define operações de logging em diferentes níveis
    para rastreamento e debugging do sistema.
    """

    @abstractmethod
    def debug(self, mensagem: str, **kwargs: Any) -> None:
        """Registra mensagem de debug."""

    @abstractmethod
    def info(self, mensagem: str, **kwargs: Any) -> None:
        """Registra mensagem informativa."""

    @abstractmethod
    def warning(
        self, mensagem: str, **kwargs: Any
    ) -> None:
        """Registra aviso."""

    @abstractmethod
    def error(
        self, mensagem: str, **kwargs: Any
    ) -> None:
        """Registra erro."""

    @abstractmethod
    def critical(
        self, mensagem: str, **kwargs: Any
    ) -> None:
        """Registra erro crítico."""
