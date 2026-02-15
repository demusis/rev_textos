"""
Agentes de IA para revisão de textos estruturados.

Implementações concretas dos agentes de revisão,
validação, consistência e síntese.
"""

import json
import logging
from typing import Dict, Any, List

from ...core.interfaces.services.i_ai_agent import (
    IAIAgent,
)
from ...core.entities.secao import Secao
from ...core.entities.revisao import Revisao
from ...core.entities.erro import Erro
from ...core.entities.correcao import Correcao
from ...core.enums.tipo_erro import TipoErro
from ...core.exceptions.agent_exceptions import (
    InvalidResponseException,
)
from .gemini_gateway import GeminiGateway
from .prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class AgenteRevisor(IAIAgent):
    """
    Agente de revisão de texto.

    Realiza revisão gramatical, técnica e estrutural
    usando o modelo Gemini.
    """

    def __init__(
        self,
        gateway: GeminiGateway,
        prompt_builder: PromptBuilder,
        tipo_revisao: str = "revisao_gramatical",
    ) -> None:
        self._gateway = gateway
        self._prompt_builder = prompt_builder
        self._tipo_revisao = tipo_revisao

    async def processar(
        self,
        secao: Secao,
        configuracao: Dict[str, Any],
    ) -> Revisao:
        """Processa seção com revisão de texto."""
        tipo = configuracao.get(
            "tipo", self._tipo_revisao
        )
        temperatura = configuracao.get(
            "temperatura", 0.3
        )
        max_tokens = configuracao.get(
            "max_tokens", 8192
        )

        mock_tag = " [MOCK]" if self._gateway._modo_mock else ""
        logger.info(
            f"━━━ INÍCIO fase '{tipo}'{mock_tag} "
            f"| Seção: '{secao.titulo}' "
            f"| Tamanho: {len(secao.conteudo_original)} chars"
        )

        # Construir prompt
        texto_para_revisao = configuracao.get(
            "texto_entrada", secao.conteudo_original
        )
        prompt = self._prompt_builder.construir(
            tipo, texto=texto_para_revisao
        )

        logger.info(
            f"    Enviando {len(prompt)} chars ao Gemini..."
        )

        # Chamar API
        resposta = await self._gateway.gerar_conteudo(
            prompt=prompt,
            temperatura=temperatura,
            max_tokens=max_tokens,
            origem=self.obter_nome(),
        )

        logger.info(
            f"    Resposta recebida: {len(resposta)} chars"
        )
        logger.info(
            f"━━━ FIM fase '{tipo}'{mock_tag} "
            f"| Seção: '{secao.titulo}'"
        )

        # Parsear resposta
        return self._parsear_resposta(resposta, secao)

    async def gerar_sintese(
        self, contexto: Dict[str, Any]
    ) -> str:
        """Gera síntese dos resultados."""
        mock_tag = " [MOCK]" if self._gateway._modo_mock else ""
        logger.info(
            f"━━━ INÍCIO fase 'síntese'{mock_tag}"
        )
        prompt = self._prompt_builder.construir(
            "sintese", dados=json.dumps(
                contexto, ensure_ascii=False
            )
        )
        resultado = await self._gateway.gerar_conteudo(
            prompt=prompt, temperatura=0.5, origem=f"{self.obter_nome()}_sintese"
        )
        logger.info(
            f"━━━ FIM fase 'síntese'{mock_tag}"
        )
        return resultado

    def _parsear_resposta(
        self, resposta: str, secao: Secao
    ) -> Revisao:
        """
        Parseia resposta JSON da API em Revisao.

        Args:
            resposta: Resposta da API (JSON)
            secao: Seção revisada

        Returns:
            Entidade Revisao preenchida
        """
        revisao = Revisao(
            numero_iteracao=0,
            texto_entrada=secao.conteudo_original,
            agente=self.obter_nome(),
        )

        try:
            # Limpar eventual markdown
            json_str = resposta
            if "```json" in json_str:
                json_str = json_str.split(
                    "```json"
                )[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split(
                    "```"
                )[1].split("```")[0]

            dados = json.loads(json_str.strip())

            # Extrair erros
            for erro_data in dados.get("erros", []):
                tipo = self._mapear_tipo_erro(
                    erro_data.get("tipo", "outro")
                )
                erro = Erro(
                    tipo=tipo,
                    descricao=erro_data.get(
                        "justificativa",
                        erro_data.get("tipo", ""),
                    ),
                    trecho_original=erro_data.get(
                        "trecho_original", ""
                    ),
                    sugestao_correcao=erro_data.get(
                        "sugestao_correcao", ""
                    ),
                    severidade=min(
                        5,
                        max(
                            1,
                            erro_data.get(
                                "severidade", 1
                            ),
                        ),
                    ),
                    agente_origem=self.obter_nome(),
                )
                revisao.adicionar_erro(erro)

                correcao = Correcao(
                    texto_original=erro_data.get(
                        "trecho_original", ""
                    ),
                    texto_corrigido=erro_data.get(
                        "sugestao_correcao", ""
                    ),
                    justificativa=erro_data.get(
                        "justificativa", ""
                    ),
                    agente_origem=self.obter_nome(),
                )
                revisao.adicionar_correcao(correcao)

            # Texto revisado
            revisao.texto_saida = dados.get(
                "texto_revisado",
                secao.conteudo_original,
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(
                f"Falha ao parsear resposta JSON: {e} "
                f"| Resposta (trecho): "
                f"{resposta[:200]!r}"
            )
            # Não engolir silenciosamente — propagar erro
            # para que a iteração saiba que a resposta falhou
            raise InvalidResponseException(
                f"A resposta da IA não é um JSON válido. "
                f"Isso geralmente ocorre quando a resposta "
                f"foi truncada (texto muito longo). "
                f"Detalhes: {e}"
            )

        return revisao

    def _mapear_tipo_erro(
        self, tipo_str: str
    ) -> TipoErro:
        """Mapeia string de tipo para enum TipoErro."""
        mapa = {
            "gramatical": TipoErro.GRAMATICAL,
            "ortografico": TipoErro.GRAMATICAL,
            "concordancia": TipoErro.GRAMATICAL,
            "tecnico": TipoErro.TECNICO,
            "inconsistencia": TipoErro.CONSISTENCIA,
            "consistencia": TipoErro.CONSISTENCIA,
            "terminologia": TipoErro.TECNICO,
            "estrutural": TipoErro.FORMATACAO,
            "coesao": TipoErro.LOGICO,
            "clareza": TipoErro.LOGICO,
            "formatacao": TipoErro.FORMATACAO,
            "fundamentacao": TipoErro.TECNICO,
            "referencia": TipoErro.REFERENCIA,
            "numerico": TipoErro.NUMERICO,
            "logico": TipoErro.LOGICO,
            "omissao": TipoErro.OMISSAO,
            "juridico": TipoErro.TECNICO,
        }
        return mapa.get(
            tipo_str.lower(), TipoErro.OUTRO
        )

    def obter_nome(self) -> str:
        return f"revisor_{self._tipo_revisao}"

    def obter_descricao(self) -> str:
        return (
            f"Agente de revisão: {self._tipo_revisao}"
        )


class AgenteValidador(IAIAgent):
    """
    Agente validador de correções.

    Verifica se as correções propostas pelo
    agente revisor são adequadas.
    """

    def __init__(
        self,
        gateway: GeminiGateway,
        prompt_builder: PromptBuilder,
    ) -> None:
        self._gateway = gateway
        self._prompt_builder = prompt_builder

    async def processar(
        self,
        secao: Secao,
        configuracao: Dict[str, Any],
    ) -> Revisao:
        """Valida correções propostas."""
        mock_tag = " [MOCK]" if self._gateway._modo_mock else ""
        logger.info(
            f"━━━ INÍCIO fase 'validação'{mock_tag} "
            f"| Seção: '{secao.titulo}'"
        )
        prompt = self._prompt_builder.construir(
            "validacao",
            texto_original=configuracao.get(
                "texto_original", ""
            ),
            texto_revisado=configuracao.get(
                "texto_revisado", ""
            ),
            correcoes=json.dumps(
                configuracao.get(
                    "erros_encontrados", []
                ),
                ensure_ascii=False,
            ),
        )

        resposta = await self._gateway.gerar_conteudo(
            prompt=prompt, temperatura=0.2, origem=self.obter_nome()
        )

        logger.info(
            f"━━━ FIM fase 'validação'{mock_tag} "
            f"| Seção: '{secao.titulo}'"
        )

        revisao = Revisao(
            numero_iteracao=0,
            texto_entrada=secao.conteudo_original,
            agente=self.obter_nome(),
            texto_saida=resposta,
        )
        return revisao

    async def gerar_sintese(
        self, contexto: Dict[str, Any]
    ) -> str:
        return "Validação concluída."

    def obter_nome(self) -> str:
        return "validador"

    def obter_descricao(self) -> str:
        return "Agente validador de correções"


class AgenteConsistencia(IAIAgent):
    """
    Agente de verificação de consistência.

    Analisa coerência entre seções do texto.
    """

    def __init__(
        self,
        gateway: GeminiGateway,
        prompt_builder: PromptBuilder,
    ) -> None:
        self._gateway = gateway
        self._prompt_builder = prompt_builder

    async def processar(
        self,
        secao: Secao,
        configuracao: Dict[str, Any],
    ) -> Revisao:
        """Não utilizado diretamente pelo agente de consistência."""
        return Revisao(
            numero_iteracao=0,
            texto_entrada=secao.conteudo_original,
            agente=self.obter_nome(),
        )

    async def gerar_sintese(
        self, contexto: Dict[str, Any]
    ) -> str:
        """Gera análise de consistência."""
        mock_tag = " [MOCK]" if self._gateway._modo_mock else ""
        logger.info(
            f"━━━ INÍCIO fase 'consistência'{mock_tag} "
            f"| {len(contexto.get('secoes', []))} seções"
        )
        secoes_str = json.dumps(
            contexto.get("secoes", []),
            ensure_ascii=False,
        )
        prompt = self._prompt_builder.construir(
            "consistencia", secoes=secoes_str
        )
        resultado = await self._gateway.gerar_conteudo(
            prompt=prompt, temperatura=0.2, origem=self.obter_nome()
        )
        logger.info(
            f"━━━ FIM fase 'consistência'{mock_tag}"
        )
        return resultado

    def obter_nome(self) -> str:
        return "consistencia"

    def obter_descricao(self) -> str:
        return (
            "Agente de verificação de consistência"
        )
