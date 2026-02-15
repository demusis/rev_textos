"""
Interface do repositório de textos estruturados.

Define o contrato para persistência e recuperação
de entidades TextoEstruturado.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ...entities.texto_estruturado import TextoEstruturado


class ITextoRepository(ABC):
    """
    Interface para repositório de textos.

    Define operações CRUD e consultas para textos
    persistidos no sistema.
    """

    @abstractmethod
    def salvar(self, texto: TextoEstruturado) -> None:
        """
        Persiste um texto no repositório.

        Args:
            texto: Texto a ser salvo
        """

    @abstractmethod
    def buscar_por_hash(
        self, hash_arquivo: str
    ) -> Optional[TextoEstruturado]:
        """
        Busca um texto pelo hash do arquivo.

        Args:
            hash_arquivo: Hash SHA-256 do arquivo

        Returns:
            TextoEstruturado encontrado ou None
        """

    @abstractmethod
    def listar_todos(self) -> List[TextoEstruturado]:
        """
        Lista todos os textos no repositório.

        Returns:
            Lista de textos
        """

    @abstractmethod
    def remover(self, hash_arquivo: str) -> None:
        """
        Remove um texto do repositório.

        Args:
            hash_arquivo: Hash do texto a remover
        """
