"""
Interface do agente de IA.

Define o contrato para agentes que realizam
revisão de conteúdo usando modelos de IA.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ...entities.secao import Secao
from ...entities.revisao import Revisao


class IAIAgent(ABC):
    """
    Interface para agentes de IA.

    Define o contrato que todos os agentes de IA
    devem implementar para participar do processo
    de revisão de textos.
    """

    @abstractmethod
    async def processar(
        self,
        secao: Secao,
        configuracao: Dict[str, Any],
    ) -> Revisao:
        """
        Processa uma seção usando o agente de IA.

        Args:
            secao: Seção a ser processada
            configuracao: Configurações do agente

        Returns:
            Resultado da revisão
        """

    @abstractmethod
    async def gerar_sintese(
        self, contexto: Dict[str, Any]
    ) -> str:
        """
        Gera síntese a partir do contexto fornecido.

        Args:
            contexto: Dados para síntese

        Returns:
            Texto da síntese gerada
        """

    @abstractmethod
    def obter_nome(self) -> str:
        """
        Retorna o nome do agente.

        Returns:
            Nome identificador do agente
        """

    @abstractmethod
    def obter_descricao(self) -> str:
        """
        Retorna a descrição do agente.

        Returns:
            Descrição das capacidades
        """
