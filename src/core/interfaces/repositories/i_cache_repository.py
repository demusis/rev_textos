"""
Interface do repositório de cache.

Define o contrato para armazenamento em cache de
respostas da API e resultados de processamento.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ICacheRepository(ABC):
    """
    Interface para repositório de cache.

    Define operações para cache de respostas
    e resultados intermediários.
    """

    @abstractmethod
    async def obter(self, chave: str) -> Optional[Any]:
        """
        Obtém valor do cache.

        Args:
            chave: Chave de busca

        Returns:
            Valor armazenado ou None se expirado/inexistente
        """

    @abstractmethod
    async def armazenar(
        self,
        chave: str,
        valor: Any,
        ttl_segundos: int = 3600,
    ) -> None:
        """
        Armazena valor no cache.

        Args:
            chave: Chave de armazenamento
            valor: Valor a armazenar
            ttl_segundos: Tempo de vida em segundos
        """

    @abstractmethod
    async def remover(self, chave: str) -> None:
        """
        Remove valor do cache.

        Args:
            chave: Chave a remover
        """

    @abstractmethod
    async def limpar(self) -> None:
        """Remove todos os valores do cache."""

    @abstractmethod
    async def contem(self, chave: str) -> bool:
        """
        Verifica se chave existe no cache.

        Args:
            chave: Chave a verificar

        Returns:
            True se existir e não estiver expirada
        """
