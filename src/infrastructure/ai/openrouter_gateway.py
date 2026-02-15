"""
Gateway de comunicação com a API do OpenRouter.

Suporta centenas de modelos de diversos provedores
via API compatível com OpenAI.
"""

import logging
import time
import hashlib
import json
from typing import Optional, List, Dict, Any

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

from ...core.interfaces.gateways.i_ai_gateway import IAIGateway
from ...core.exceptions.agent_exceptions import (
    APIException,
    RateLimitException,
    TimeoutException,
    InvalidResponseException,
)

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterGateway(IAIGateway):
    """
    Gateway concreto para a API do OpenRouter.

    Usa a API compatível com OpenAI para acessar
    modelos de diversos provedores (Google, Meta,
    Mistral, Anthropic, etc.) via OpenRouter.

    Attributes:
        _api_key: Chave de API do OpenRouter
        _model_name: Nome do modelo (ex: google/gemini-2.5-flash-preview-05-20)
        _timeout: Timeout em segundos
        _cache: Cache local de respostas
        _metricas: Métricas acumuladas
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "google/gemini-2.5-flash-preview-05-20",
        timeout: int = 120,
    ) -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._timeout = timeout

        self._cache: Dict[str, str] = {}
        self._metricas: Dict[str, Any] = {
            "total_requests": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "total_erros": 0,
            "tempo_total_seg": 0.0,
        }
        self._modo_mock = False

        if httpx is None:
            logger.error("Biblioteca 'httpx' não instalada.")

    async def gerar_conteudo(
        self,
        prompt: str,
        contexto: Optional[str] = None,
        temperatura: float = 0.7,
        max_tokens: int = 2048,
        stop_sequences: Optional[List[str]] = None,
        origem: str = "Geral",
    ) -> str:
        if httpx is None:
            raise APIException(
                "Biblioteca 'httpx' não está instalada.\n\n"
                "Execute: pip install httpx\n"
                "Ou altere o provedor em Configurações."
            )

        if not self._api_key:
            raise APIException(
                "Chave de API do OpenRouter não configurada.\n\n"
                "Obtenha uma chave em: openrouter.ai/keys\n"
                "Configure em: Configurações → IA / Provedores → OpenRouter"
            )

        # Verificar cache
        dados_cache = (
            f"{prompt}|{contexto}|{temperatura}|{self._model_name}"
        )
        cache_key = hashlib.md5(
            dados_cache.encode()
        ).hexdigest()

        if cache_key in self._cache:
            logger.debug(
                f"[{origem}] Resposta obtida do cache (OpenRouter)"
            )
            return self._cache[cache_key]

        # Construir mensagens
        messages: List[Dict[str, str]] = []
        if contexto:
            messages.append(
                {"role": "system", "content": contexto}
            )
        messages.append({"role": "user", "content": prompt})

        # Payload
        payload: Dict[str, Any] = {
            "model": self._model_name,
            "messages": messages,
            "temperature": temperatura,
            "max_tokens": max_tokens,
        }
        if stop_sequences:
            payload["stop"] = stop_sequences

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/revisor-textos",
            "X-Title": "Revisor de Textos Estruturados",
        }

        inicio = time.time()
        try:
            logger.info(
                f"[{origem}] 📡 OpenRouter: "
                f"{self._model_name} | Temp: {temperatura}"
            )

            async with httpx.AsyncClient(
                timeout=self._timeout
            ) as client:
                response = await client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                )

            elapsed = time.time() - inicio

            # Tratar erros HTTP
            if response.status_code == 401:
                raise APIException(
                    "Chave de API do OpenRouter inválida.\n\n"
                    "Verifique sua chave em Configurações "
                    "→ IA / Provedores → OpenRouter.\n"
                    "Obtenha uma chave em: openrouter.ai/keys"
                )
            elif response.status_code == 429:
                raise RateLimitException(
                    "Limite de requisições do OpenRouter atingido.\n"
                    "Aguarde alguns segundos e tente novamente."
                )
            elif response.status_code == 402:
                raise APIException(
                    "Créditos insuficientes no OpenRouter.\n\n"
                    "Verifique seu saldo em openrouter.ai/credits\n"
                    "ou use modelos gratuitos (com sufixo :free)."
                )
            elif response.status_code >= 400:
                try:
                    err_body = response.json()
                    err_msg = err_body.get("error", {}).get(
                        "message", response.text[:200]
                    )
                except Exception:
                    err_msg = response.text[:200]
                raise APIException(
                    f"Erro na API OpenRouter ({response.status_code}): "
                    f"{err_msg}"
                )

            data = response.json()

            # Extrair resposta
            choices = data.get("choices", [])
            if not choices:
                raise APIException(
                    "A API do OpenRouter retornou resposta vazia.\n\n"
                    "Possíveis causas:\n"
                    "• Modelo não suporta o tipo de prompt enviado\n"
                    "• Tente outro modelo em Configurações"
                )

            resultado = (
                choices[0]
                .get("message", {})
                .get("content", "")
            )

            if not resultado:
                raise APIException(
                    "A API do OpenRouter retornou conteúdo vazio.\n\n"
                    "Tente outro modelo em Configurações."
                )

            # Registrar métricas
            self._metricas["total_requests"] += 1
            self._metricas["tempo_total_seg"] += elapsed

            usage = data.get("usage", {})
            if usage:
                self._metricas["total_tokens_input"] += usage.get(
                    "prompt_tokens", 0
                )
                self._metricas["total_tokens_output"] += usage.get(
                    "completion_tokens", 0
                )

            # Cache
            self._cache[cache_key] = resultado
            return resultado

        except (APIException, RateLimitException):
            self._metricas["total_erros"] += 1
            raise
        except httpx.TimeoutException:
            self._metricas["total_erros"] += 1
            raise TimeoutException(
                "A conexão com o OpenRouter expirou.\n\n"
                "Verifique sua internet e tente novamente."
            )
        except httpx.ConnectError:
            self._metricas["total_erros"] += 1
            raise TimeoutException(
                "Não foi possível conectar ao OpenRouter.\n\n"
                "Possíveis causas:\n"
                "• Sem conexão com a internet\n"
                "• Serviço temporariamente indisponível"
            )
        except Exception as e:
            self._metricas["total_erros"] += 1
            raise APIException(
                f"Erro inesperado OpenRouter: {e}"
            )

    def obter_metricas(self) -> Dict[str, Any]:
        return dict(self._metricas)

    def limpar_cache(self) -> None:
        self._cache.clear()

    def resetar_metricas(self) -> None:
        for key in self._metricas:
            self._metricas[key] = (
                0 if isinstance(self._metricas[key], int) else 0.0
            )

    def obter_info_modelo(self) -> Dict[str, str]:
        """Retorna informações sobre o modelo."""
        return {
            "provedor": "OpenRouter",
            "modelo": self._model_name,
        }

    def listar_modelos(self) -> List[str]:
        """
        Lista modelos disponíveis na API do OpenRouter.

        Returns:
            Lista de IDs de modelos disponíveis
        """
        if httpx is None:
            logger.warning("Biblioteca 'httpx' não instalada.")
            return []

        if not self._api_key:
            logger.warning(
                "Chave do OpenRouter não configurada."
            )
            return []

        try:
            with httpx.Client(timeout=15) as client:
                response = client.get(
                    f"{OPENROUTER_BASE_URL}/models",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                    },
                )

            if response.status_code != 200:
                logger.error(
                    f"OpenRouter /models HTTP {response.status_code}"
                )
                return []

            data = response.json()
            modelos = sorted(
                m["id"]
                for m in data.get("data", [])
                if "id" in m
            )
            logger.info(
                f"OpenRouter: {len(modelos)} modelos disponíveis"
            )
            return modelos

        except Exception as e:
            logger.error(
                f"Erro ao listar modelos OpenRouter: {e}"
            )
            return []
