"""
Interface do repositório de configurações.

Define o contrato para carregamento e persistência
de configurações do sistema.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IConfigRepository(ABC):
    """
    Interface para repositório de configurações.

    Define operações para gerenciamento de configurações
    do sistema e dos prompts de IA.
    """

    @abstractmethod
    def carregar_configuracao(self) -> Dict[str, Any]:
        """
        Carrega configuração completa do sistema.

        Returns:
            Dicionário com todas as configurações
        """

    @abstractmethod
    def salvar_configuracao(
        self, config: Dict[str, Any]
    ) -> None:
        """
        Salva configuração do sistema.

        Args:
            config: Dicionário de configurações
        """

    @abstractmethod
    def obter_valor(
        self, chave: str, padrao: Any = None
    ) -> Any:
        """
        Obtém valor de configuração por chave.

        Args:
            chave: Chave da configuração (dot notation)
            padrao: Valor padrão se não encontrado

        Returns:
            Valor da configuração
        """

    @abstractmethod
    def definir_valor(
        self, chave: str, valor: Any
    ) -> None:
        """
        Define valor de configuração.

        Args:
            chave: Chave da configuração
            valor: Valor a definir
        """

    @abstractmethod
    def carregar_prompt(
        self, tipo: str
    ) -> Optional[Dict[str, Any]]:
        """
        Carrega template de prompt por tipo.

        Args:
            tipo: Tipo do prompt (ex: "revisao_tecnica")

        Returns:
            Dicionário com template e parâmetros
        """
