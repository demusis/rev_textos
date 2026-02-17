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
from .prompt_builder import PromptBuilder
from ...core.interfaces.gateways.i_ai_gateway import IAIGateway

logger = logging.getLogger(__name__)


class AgenteRevisor(IAIAgent):
    """
    Agente de revisão de texto.

    Realiza revisão gramatical, técnica e estrutural
    usando modelos de IA.
    """

    def __init__(
        self,
        gateway: IAIGateway,
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

        info_ia = self._gateway.obter_info_modelo()
        provedor = info_ia.get("provedor", "IA")

        logger.info(
            f"    Enviando {len(prompt)} chars ao {provedor}..."
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
            # Seleção robusta do bloco JSON (caso a IA mande conversa antes/depois)
            json_str = resposta.strip()
            
            # Tenta encontrar o primeiro '{' e o último '}'
            idx_start = json_str.find('{')
            idx_end = json_str.rfind('}')
            
            if idx_start != -1 and idx_end != -1:
                json_str = json_str[idx_start:idx_end+1]
            
            # Limpar blocos de código markdown se ainda existirem
            if "```json" in json_str:
                json_str = json_str.split("```json")[-1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[-1].split("```")[0]

            dados = json.loads(json_str.strip())

            # Extrair erros
            for erro_data in dados.get("erros", []):
                tipo = self._mapear_tipo_erro(
                    erro_data.get("tipo", "outro")
                )
                # Fallback em cascata para garantir descrição não vazia
                descricao = (
                    erro_data.get("justificativa") or 
                    erro_data.get("descricao") or 
                    erro_data.get("tipo") or 
                    "Ajuste sugerido pela IA"
                )
                
                # Garantir que trecho_original tenha algo (fallback pro texto da seção se nulo)
                trecho_orig = erro_data.get("trecho_original") or ""
                sugestao = erro_data.get("sugestao_correcao") or ""

                erro = Erro(
                    tipo=tipo,
                    descricao=descricao,
                    trecho_original=trecho_orig,
                    sugestao_correcao=sugestao,
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
                    texto_original=trecho_orig,
                    texto_corrigido=sugestao,
                    justificativa=descricao,
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
        gateway: IAIGateway,
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
        gateway: IAIGateway,
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
        return self._formatar_consistencia(resultado)

    def _formatar_consistencia(self, resposta_json: str) -> str:
        """Formata resposta JSON em Markdown legível."""
        try:
            # Limpeza básica de markdown
            json_str = resposta_json.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[-1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[-1].split("```")[0]
            
            dados = json.loads(json_str.strip())
            
            lines = []
            
            # Resumo
            if "resumo" in dados:
                lines.append(f"**Resumo da Análise**\n{dados['resumo']}\n")
            
            # Status
            consistente = dados.get("consistente", False)
            status_exibicao = "✅ Consistente" if consistente else "⚠️ Inconsistências Encontradas"
            lines.append(f"**Status Global**: {status_exibicao}\n")
            
            # Inconsistências
            inconsistencias = dados.get("inconsistencias", [])
            if inconsistencias:
                lines.append("**Detalhes:**\n")
                for i, inc in enumerate(inconsistencias, 1):
                    sev = inc.get("severidade", 1)
                    icone = "🔴" if sev >= 4 else "🟠" if sev == 3 else "🟡"
                    
                    desc = inc.get("descricao", "Sem descrição")
                    lines.append(f"{i}. {icone} **{desc}**")
                    
                    locais = []
                    if "secao_1" in inc: locais.append(f"'{inc['secao_1']}'")
                    if "secao_2" in inc: locais.append(f"'{inc['secao_2']}'")
                    
                    if locais:
                        lines.append(f"   - *Local*: {' e '.join(locais)}")
                    
                    if "sugestao" in inc:
                        lines.append(f"   - *Sugestão*: {inc['sugestao']}")
                    lines.append("")
            
            return "\n".join(lines)

        except Exception:
            # Se falhar o parse, retorna o original (fallback)
            return resposta_json

    def obter_nome(self) -> str:
        return "consistencia"

    def obter_descricao(self) -> str:
        return (
            "Agente de verificação de consistência"
        )
