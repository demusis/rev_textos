"""
Interface do gateway de IA.

Define o contrato para comunicação com APIs
de modelos de linguagem (Google Gemini).
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class IAIGateway(ABC):
    """
    Interface para gateway de comunicação com API de IA.

    Define operações de geração de conteúdo e
    gerenciamento de métricas de uso.
    """

    @abstractmethod
    async def gerar_conteudo(
        self,
        prompt: str,
        contexto: Optional[str] = None,
        temperatura: float = 0.7,
        max_tokens: int = 2048,
        stop_sequences: Optional[List[str]] = None,
    ) -> str:
        """
        Gera conteúdo usando o modelo de IA.

        Args:
            prompt: Prompt principal
            contexto: Contexto adicional
            temperatura: Temperatura (0.0-1.0)
            max_tokens: Máximo de tokens na resposta
            stop_sequences: Sequências de parada

        Returns:
            Texto gerado pelo modelo
        """

    @abstractmethod
    def obter_metricas(self) -> Dict[str, Any]:
        """
        Retorna métricas acumuladas de uso.

        Returns:
            Dicionário com métricas
        """

    @abstractmethod
    def limpar_cache(self) -> None:
        """Limpa cache de respostas."""

    @abstractmethod
    def resetar_metricas(self) -> None:
        """Reseta métricas acumuladas."""

    @abstractmethod
    def obter_info_modelo(self) -> Dict[str, str]:
        """
        Retorna informações sobre o modelo em uso.
        
        Returns:
            Dict com 'provedor' e 'modelo'
        """

    @abstractmethod
    def listar_modelos(self) -> List[str]:
        """
        Lista modelos disponíveis na API.

        Returns:
            Lista de nomes de modelos disponíveis
        """
