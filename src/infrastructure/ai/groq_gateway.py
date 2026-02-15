"""
Gateway de comunicação com a API da Groq.

Suporta modelos Llama 3, Mixtral e Gemma com extrema velocidade.
"""

import logging
import time
import hashlib
from typing import Optional, List, Dict, Any

try:
    from groq import Groq, AsyncGroq
    from groq import (
        RateLimitError,
        APIError,
        APIConnectionError,
        AuthenticationError,
    )
except ImportError:
    Groq = None  # type: ignore
    AsyncGroq = None  # type: ignore

from ...core.interfaces.gateways.i_ai_gateway import IAIGateway
from ...core.exceptions.agent_exceptions import (
    APIException,
    RateLimitException,
    TimeoutException,
    InvalidResponseException,
)

logger = logging.getLogger(__name__)


class GroqGateway(IAIGateway):
    """
    Gateway concreto para a API da Groq.
    
    Attributes:
        _client: Cliente assíncrono da Groq
        _model_name: Nome do modelo (ex: llama3-70b-8192)
        _api_key: Chave de API
        _timeout: Timeout em segundos
        _cache: Cache local de respostas
        _metricas: Métricas acumuladas
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "llama3-70b-8192",
        timeout: int = 60,
    ) -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._timeout = timeout
        
        self._client = None
        if AsyncGroq:
            self._client = AsyncGroq(api_key=api_key, timeout=timeout)
        else:
            logger.warning("Biblioteca 'groq' não instalada.")

        self._cache: Dict[str, str] = {}
        self._metricas: Dict[str, Any] = {
            "total_requests": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "total_erros": 0,
            "tempo_total_seg": 0.0,
        }
        self._modo_mock = False

    async def gerar_conteudo(
        self,
        prompt: str,
        contexto: Optional[str] = None,
        temperatura: float = 0.7,
        max_tokens: int = 2048,
        stop_sequences: Optional[List[str]] = None,
        origem: str = "Geral",
    ) -> str:
        if not self._client:
            raise APIException(
                "Biblioteca 'groq' não está instalada.\n\n"
                "Execute: pip install groq\n"
                "Ou altere o provedor para Gemini em Configurações."
            )

        # Verificar cache
        dados_cache = f"{prompt}|{contexto}|{temperatura}|{self._model_name}"
        cache_key = hashlib.md5(dados_cache.encode()).hexdigest()
        
        if cache_key in self._cache:
            logger.debug(f"[{origem}] Resposta obtida do cache (Groq)")
            return self._cache[cache_key]

        # Construir mensagens
        messages = []
        if contexto:
            messages.append({"role": "system", "content": contexto})
        messages.append({"role": "user", "content": prompt})

        inicio = time.time()
        try:
            logger.info(f"[{origem}] 📡 Groq: {self._model_name} | Temp: {temperatura}")
            
            chat_completion = await self._client.chat.completions.create(
                messages=messages,
                model=self._model_name,
                temperature=temperatura,
                max_tokens=max_tokens,
                stop=stop_sequences,
            )

            elapsed = time.time() - inicio
            resultado = chat_completion.choices[0].message.content or ""
            
            if not resultado:
                raise APIException(
                    "A API da Groq retornou uma resposta vazia.\n\n"
                    "Possíveis causas:\n"
                    "• Modelo não suporta o tipo de prompt enviado\n"
                    "• Tente outro modelo em Configurações"
                )

            # Registrar métricas
            self._metricas["total_requests"] += 1
            self._metricas["tempo_total_seg"] += elapsed
            
            if chat_completion.usage:
                self._metricas["total_tokens_input"] += chat_completion.usage.prompt_tokens
                self._metricas["total_tokens_output"] += chat_completion.usage.completion_tokens

            # Cache
            self._cache[cache_key] = resultado
            
            return resultado

        except RateLimitError as e:
            self._metricas["total_erros"] += 1
            raise RateLimitException(
                "Limite de requisições da Groq atingido.\n"
                "Aguarde alguns segundos e tente novamente."
            )
        except AuthenticationError as e:
            self._metricas["total_erros"] += 1
            raise APIException(
                "Chave de API da Groq inválida ou não configurada.\n\n"
                "Verifique sua chave em Configurações → IA / Provedores → Groq.\n"
                "Obtenha uma chave em: console.groq.com"
            )
        except APIConnectionError as e:
            self._metricas["total_erros"] += 1
            raise TimeoutException(
                "Não foi possível conectar à API da Groq.\n\n"
                "Possíveis causas:\n"
                "• Chave de API não configurada\n"
                "• Sem conexão com a internet\n"
                "• Serviço da Groq temporariamente indisponível"
            )
        except APIError as e:
            self._metricas["total_erros"] += 1
            msg = str(e)
            if "decommissioned" in msg:
                raise APIException(
                    "O modelo selecionado foi descontinuado pela Groq.\n\n"
                    "Abra Configurações → IA / Provedores → Groq\n"
                    "e selecione outro modelo da lista."
                )
            raise APIException(f"Erro na API Groq: {e}")
        except Exception as e:
            self._metricas["total_erros"] += 1
            raise APIException(f"Erro inesperado Groq: {e}")

    def obter_metricas(self) -> Dict[str, Any]:
        return dict(self._metricas)

    def limpar_cache(self) -> None:
        self._cache.clear()

    def resetar_metricas(self) -> None:
        for key in self._metricas:
            self._metricas[key] = 0 if isinstance(self._metricas[key], int) else 0.0

    def obter_info_modelo(self) -> Dict[str, str]:
        """Retorna informações sobre o modelo."""
        return {
            "provedor": "Groq",
            "modelo": self._model_name
        }

    def listar_modelos(self) -> List[str]:
        """
        Lista modelos disponíveis na API da Groq.

        Returns:
            Lista de nomes de modelos disponíveis
        """
        if not Groq:
            logger.warning("Biblioteca 'groq' não instalada.")
            return []

        if not self._api_key:
            logger.warning("Chave da Groq não configurada.")
            return []

        try:
            client = Groq(api_key=self._api_key)
            response = client.models.list()
            modelos = sorted(
                m.id for m in response.data
                if hasattr(m, "id")
            )
            logger.info(
                f"Groq: {len(modelos)} modelos disponíveis"
            )
            return modelos
        except Exception as e:
            logger.error(f"Erro ao listar modelos Groq: {e}")
            return []
