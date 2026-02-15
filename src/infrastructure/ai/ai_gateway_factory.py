"""
Fábrica de Gateways de IA.

Responsável por instanciar o gateway correto (Gemini, Groq, etc.)
com base na configuração do sistema.
"""

import logging
from typing import Dict, Any, Optional

from ...core.interfaces.gateways.i_ai_gateway import IAIGateway
from .gemini_gateway import GeminiGateway
from .groq_gateway import GroqGateway
from .openrouter_gateway import OpenRouterGateway

logger = logging.getLogger(__name__)


class AIGatewayFactory:
    """
    Factory para criar instâncias de IAIGateway.
    """

    @staticmethod
    def criar(
        config: Dict[str, Any]
    ) -> IAIGateway:
        """
        Cria um gateway com base na configuração.

        Args:
            config: Dicionário de configuração contendo 'provider' e 'api_keys'.

        Returns:
            Instância de IAIGateway configurada.
        """
        provider = config.get("provider", "gemini").lower()
        api_keys = config.get("api_keys", {})
        
        # Fallback para chave antiga se não houver dict de chaves
        if not api_keys:
            old_key = config.get("api_key_gemini")
            if old_key:
                api_keys["gemini"] = old_key

        logger.info(f"Criando gateway de IA para provedor: {provider}")

        if provider == "groq":
            key = api_keys.get("groq")
            if not key:
                logger.warning("Chave da Groq não encontrada. Usando modo mock/erro.")
                # Pode retornar um Mock ou deixar explodir erro no init do gateway
            
            return GroqGateway(
                api_key=key or "",
                model_name=config.get("model_groq", "llama-3.3-70b-versatile"),
                timeout=config.get("timeout_groq", 60)
            )

        elif provider == "gemini":
            key = api_keys.get("gemini")
            return GeminiGateway(
                api_key=key or "",
                model_name=config.get("model_gemini", "gemini-2.0-flash"),
                modo_mock=config.get("modo_mock", False)
            )

        elif provider == "openrouter":
            key = api_keys.get("openrouter")
            if not key:
                logger.warning("Chave do OpenRouter não encontrada.")

            return OpenRouterGateway(
                api_key=key or "",
                model_name=config.get(
                    "model_openrouter",
                    "google/gemini-2.5-flash-preview-05-20",
                ),
                timeout=config.get("timeout", 120),
            )

        else:
            logger.error(f"Provedor desconhecido: {provider}. Fallback para Gemini.")
            return GeminiGateway(
                api_key=api_keys.get("gemini", ""),
                model_name="gemini-2.0-flash"
            )

    FALLBACK_GEMINI = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ]

    FALLBACK_GROQ = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "mixtral-8x7b-32768",
    ]

    FALLBACK_OPENROUTER = [
        "google/gemini-2.5-flash-preview-05-20",
        "meta-llama/llama-3.3-70b-instruct:free",
        "mistralai/mistral-small-3.1-24b-instruct:free",
        "qwen/qwen3-235b-a22b:free",
    ]

    @staticmethod
    def listar_modelos(
        provider: str, api_key: str
    ) -> list:
        """
        Lista modelos disponíveis para um provedor.

        Cria gateway temporário e consulta a API.
        Retorna fallback hardcoded se falhar.

        Args:
            provider: Nome do provedor ('gemini' ou 'groq')
            api_key: Chave de API

        Returns:
            Lista de nomes de modelos
        """
        provider = provider.lower()
        try:
            if provider == "groq":
                gw = GroqGateway(
                    api_key=api_key or "",
                    timeout=15,
                )
                modelos = gw.listar_modelos()
                return modelos if modelos else AIGatewayFactory.FALLBACK_GROQ

            elif provider == "gemini":
                gw = GeminiGateway(
                    api_key=api_key or "",
                    modo_mock=not bool(api_key),
                )
                modelos = gw.listar_modelos()
                return modelos if modelos else AIGatewayFactory.FALLBACK_GEMINI

            elif provider == "openrouter":
                gw = OpenRouterGateway(
                    api_key=api_key or "",
                    timeout=15,
                )
                modelos = gw.listar_modelos()
                return modelos if modelos else AIGatewayFactory.FALLBACK_OPENROUTER

        except Exception as e:
            logger.warning(
                f"Falha ao listar modelos de {provider}: {e}"
            )

        # Fallback
        if provider == "groq":
            return list(AIGatewayFactory.FALLBACK_GROQ)
        if provider == "openrouter":
            return list(AIGatewayFactory.FALLBACK_OPENROUTER)
        return list(AIGatewayFactory.FALLBACK_GEMINI)
