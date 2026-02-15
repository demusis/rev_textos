"""
Gateway de comunicação com a API do Google Gemini.

Implementa a interface IAIGateway com retry automático,
rate limiting, cache de respostas e métricas de uso.
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Optional, List, Dict, Any

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # type: ignore

from ...core.interfaces.gateways.i_ai_gateway import (
    IAIGateway,
)
from ...core.exceptions.agent_exceptions import (
    APIException,
    TimeoutException,
    RateLimitException,
    InvalidResponseException,
)

logger = logging.getLogger(__name__)


class GeminiGateway(IAIGateway):
    """
    Gateway concreto para a API do Google Gemini.

    Implementa comunicação com retry exponencial,
    rate limiting, cache local e coleta de métricas.

    Attributes:
        _model: Instância do modelo Gemini
        _api_key: Chave de API
        _model_name: Nome do modelo
        _max_retries: Máximo de tentativas
        _timeout: Timeout em segundos
        _cache: Cache local de respostas
        _metricas: Métricas acumuladas
        _rate_limit: Controle de taxa
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash",
        max_retries: int = 3,
        timeout: int = 120,
        requests_per_minute: int = 60,
        modo_mock: bool = False,
    ) -> None:
        """
        Inicializa o gateway.

        Args:
            api_key: Chave da API Gemini
            model_name: Nome do modelo a usar
            max_retries: Tentativas máximas
            timeout: Timeout em segundos
            requests_per_minute: Limite de requisições
            modo_mock: Força modo mock (sem API)
        """
        self._api_key = api_key
        self._model_name = model_name
        self._max_retries = max_retries
        self._timeout = timeout
        self._requests_per_minute = (
            requests_per_minute
        )
        self._modo_mock = modo_mock

        self._cache: Dict[str, str] = {}
        self._metricas: Dict[str, Any] = {
            "total_requests": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "total_erros": 0,
            "tempo_total_seg": 0.0,
        }
        self._request_timestamps: List[float] = []
        self._model = None

        if not self._modo_mock:
            self._inicializar_modelo()
        else:
            logger.info("Gateway em modo mock")

    def _formatar_erro(self, e: Exception) -> str:
        """Formata erros da API de forma amigável e sintética."""
        mensagem = str(e)
        
        # Rate Limit (429)
        if "429" in mensagem or "quota" in mensagem.lower():
            return (
                "Limite de uso da IA excedido.\n\n"
                "Aguarde cerca de 1 minuto antes de tentar novamente "
                "ou verifique se atingiu o limite diário da sua chave."
            )
            
        # Chave Inválida (400)
        if "400" in mensagem and ("key" in mensagem.lower() or "invalid" in mensagem.lower()):
            return (
                "Chave de API inválida ou expirada.\n\n"
                "Por favor, verifique a chave configurada em 'Configurações'."
            )
            
        # Timeout
        if "timeout" in mensagem.lower() or "deadline" in mensagem.lower():
            return "A conexão com a IA demorou demais. Verifique sua internet e tente novamente."
            
        # Erros Genéricos de Rede
        if "connect" in mensagem.lower() or "unreachable" in mensagem.lower():
            return "Não foi possível conectar aos servidores da IA. Verifique sua conexão."

        # Limpeza para outros erros (remove prefixos técnicos)
        if ":" in mensagem:
            partes = mensagem.split(":")
            # Pega a última parte que geralmente é a mensagem real
            return partes[-1].strip()
                
        return mensagem

    def _inicializar_modelo(self) -> None:
        """Configura e inicializa o modelo Gemini."""
        if genai is None:
            logger.error(
                "google-generativeai não instalado."
            )
            return

        if not self._api_key:
            logger.error(
                "Chave de API do Gemini não configurada."
            )
            return

        try:
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel(
                model_name=self._model_name
            )
            logger.info(
                f"Modelo {self._model_name} inicializado"
            )
        except Exception as e:
            logger.error(
                f"Erro ao inicializar modelo Gemini: {e}"
            )
            self._model = None

    def listar_modelos(self) -> List[str]:
        """
        Lista modelos disponíveis na API.
        
        Returns:
            Lista de nomes de modelos (ex: gemini-pro)
        """
        if self._modo_mock or genai is None:
            return [
                "gemini-2.0-flash (mock)",
                "gemini-1.5-pro (mock)"
            ]
            
        try:
            modelos = []
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    name = m.name.replace("models/", "")
                    modelos.append(name)
            return sorted(modelos)
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []

    async def gerar_conteudo(
        self,
        prompt: str,
        contexto: Optional[str] = None,
        temperatura: float = 0.7,
        max_tokens: int = 2048,
        stop_sequences: Optional[List[str]] = None,
        origem: str = "Geral",
    ) -> str:
        """
        Gera conteúdo usando a API do Gemini.

        Implementa retry com backoff exponencial e
        cache de respostas idênticas.

        Args:
            prompt: Prompt principal
            contexto: Contexto adicional
            temperatura: Controle de criatividade
            max_tokens: Máximo de tokens na resposta
            stop_sequences: Sequências de parada

        Returns:
            Texto gerado pelo modelo

        Raises:
            APIException: Se houver erro na API
            TimeoutException: Se exceder timeout
            RateLimitException: Se exceder rate limit
        """
        if self._modo_mock:
            logger.info(
                f"[{origem}] 📡 Modelo: {self._model_name} | MODO MOCK"
            )
            logger.info(
                f"[{origem}]    Prompt: {prompt[:120]}..."
            )
            return self._mock_response(prompt)

        # Verificar cache
        cache_key = self._gerar_cache_key(
            prompt, contexto, temperatura
        )
        if cache_key in self._cache:
            logger.debug("Resposta obtida do cache")
            return self._cache[cache_key]

        # Verificar rate limit
        await self._verificar_rate_limit()

        # Construir prompt completo
        prompt_completo = prompt
        if contexto:
            prompt_completo = (
                f"Contexto:\n{contexto}\n\n"
                f"Instrução:\n{prompt}"
            )

        # Executar com retry
        for tentativa in range(
            1, self._max_retries + 1
        ):
            try:
                logger.info(
                    f"[{origem}] 📡 Modelo: {self._model_name} "
                    f"| Tentativa {tentativa}/{self._max_retries} "
                    f"| Temp: {temperatura}"
                )
                logger.info(
                    f"[{origem}]    Prompt ({len(prompt_completo)} chars): "
                    f"{prompt_completo[:120]}..."
                )
                
                resultado = await self._executar_request(
                    prompt_completo,
                    temperatura,
                    max_tokens,
                    stop_sequences,
                )

                # Armazenar em cache
                self._cache[cache_key] = resultado
                return resultado

            except RateLimitException:
                if tentativa < self._max_retries:
                    espera = 2**tentativa
                    logger.warning(
                        f"Rate limit. Aguardando "
                        f"{espera}s (tentativa "
                        f"{tentativa})"
                    )
                    await asyncio.sleep(espera)
                else:
                    raise

            except Exception as e:
                self._metricas["total_erros"] += 1
                if tentativa < self._max_retries:
                    espera = 2**tentativa
                    logger.warning(
                        f"Erro na tentativa "
                        f"{tentativa}: {e}. "
                        f"Retry em {espera}s"
                    )
                    await asyncio.sleep(espera)
                else:
                    raise APIException(
                        f"Falha após "
                        f"{self._max_retries} "
                        f"tentativas: {e}"
                    )

        raise APIException(
            "Falha inesperada no processamento"
        )

    async def _executar_request(
        self,
        prompt: str,
        temperatura: float,
        max_tokens: int,
        stop_sequences: Optional[List[str]],
    ) -> str:
        """
        Executa uma requisição à API.

        Args:
            prompt: Prompt completo
            temperatura: Temperatura
            max_tokens: Tokens máximos
            stop_sequences: Sequências de parada

        Returns:
            Texto da resposta

        Raises:
            APIException: Se houver erro
        """
        # Logar detalhes do prompt (truncado se muito longo)
        prompt_preview = prompt[:100].replace("\n", " ") + ("..." if len(prompt) > 100 else "")
        logger.debug(f"Prompt enviado: {prompt_preview}")
        
        if self._model is None:
            if genai is None:
                raise APIException(
                    "Biblioteca 'google-generativeai' não instalada.\n\n"
                    "Execute: pip install google-generativeai"
                )
            raise APIException(
                "Modelo Gemini não inicializado.\n\n"
                "Possíveis causas:\n"
                "• Chave de API não configurada ou inválida\n"
                "• Verifique em Configurações → IA / Provedores → Gemini"
            )

        inicio = time.time()

        try:
            generation_config = (
                genai.types.GenerationConfig(
                    temperature=temperatura,
                    max_output_tokens=max_tokens,
                    stop_sequences=stop_sequences or [],
                )
            )

            response = await asyncio.to_thread(
                self._model.generate_content,
                prompt,
                generation_config=generation_config,
            )

            elapsed = time.time() - inicio
            self._registrar_metricas(response, elapsed)
            self._request_timestamps.append(
                time.time()
            )

            if not response.text:
                raise InvalidResponseException(
                    "Resposta vazia da API"
                )

            return response.text

        except asyncio.TimeoutError:
            raise TimeoutException(
                f"Timeout após {self._timeout}s"
            )
        except Exception as e:
            if "429" in str(e) or "quota" in str(
                e
            ).lower():
                raise RateLimitException(
                    self._formatar_erro(e)
                )
            raise APIException(
                self._formatar_erro(e)
            )

    def _mock_response(self, prompt: str) -> str:
        """
        Gera resposta mock para desenvolvimento.

        Args:
            prompt: Prompt recebido

        Returns:
            Resposta simulada
        """
        logger.info("Usando resposta mock")
        self._metricas["total_requests"] += 1
        return (
            "[MOCK] Resposta simulada para "
            "desenvolvimento. O módulo "
            "google-generativeai não está "
            "instalado ou a API key não foi "
            "configurada."
        )

    async def _verificar_rate_limit(self) -> None:
        """
        Verifica e aplica rate limiting.

        Raises:
            RateLimitException: Se limite excedido
        """
        agora = time.time()
        # Limpar timestamps antigos (> 60s)
        self._request_timestamps = [
            ts
            for ts in self._request_timestamps
            if agora - ts < 60
        ]

        if (
            len(self._request_timestamps)
            >= self._requests_per_minute
        ):
            espera = (
                60
                - (agora - self._request_timestamps[0])
            )
            if espera > 0:
                logger.info(
                    f"Rate limit: aguardando "
                    f"{espera:.1f}s"
                )
                await asyncio.sleep(espera)

    def _gerar_cache_key(
        self,
        prompt: str,
        contexto: Optional[str],
        temperatura: float,
    ) -> str:
        """Gera chave de cache baseada nos parâmetros."""
        dados = f"{prompt}|{contexto}|{temperatura}"
        return hashlib.md5(
            dados.encode()
        ).hexdigest()

    def _registrar_metricas(
        self, response: Any, tempo: float
    ) -> None:
        """Registra métricas da requisição."""
        self._metricas["total_requests"] += 1
        self._metricas["tempo_total_seg"] += tempo

        if hasattr(response, "usage_metadata"):
            usage = response.usage_metadata
            if hasattr(usage, "prompt_token_count"):
                self._metricas[
                    "total_tokens_input"
                ] += usage.prompt_token_count
            if hasattr(
                usage, "candidates_token_count"
            ):
                self._metricas[
                    "total_tokens_output"
                ] += usage.candidates_token_count

    def obter_metricas(self) -> Dict[str, Any]:
        """Retorna métricas acumuladas de uso."""
        return dict(self._metricas)

    def limpar_cache(self) -> None:
        """Limpa cache de respostas."""
        self._cache.clear()
        logger.info("Cache limpo")

    def resetar_metricas(self) -> None:
        """Reseta métricas acumuladas."""
        for key in self._metricas:
            if isinstance(self._metricas[key], int):
                self._metricas[key] = 0
            elif isinstance(
                self._metricas[key], float
            ):
                self._metricas[key] = 0.0
        logger.info("Métricas resetadas")

    def obter_info_modelo(self) -> Dict[str, str]:
        """Retorna informações sobre o modelo."""
        return {
            "provedor": "Google Gemini",
            "modelo": self._model_name
        }
