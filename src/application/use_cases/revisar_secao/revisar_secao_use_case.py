"""
Caso de uso: Revisar Seção.

Orquestra a revisão iterativa de uma seção do texto
usando agentes de IA até atingir convergência.
"""

from typing import Optional, Dict, Any
import time

from ....core.entities.secao import Secao
from ....core.entities.texto_estruturado import TextoEstruturado
from ....core.entities.revisao import Revisao
from ....core.entities.erro import Erro
from ....core.entities.correcao import Correcao
from ....core.enums.status_texto import StatusTexto
from ....core.enums.tipo_erro import TipoErro
from ....core.interfaces.services.i_ai_agent import (
    IAIAgent,
)
from ....core.interfaces.services.i_logger import (
    ILogger,
)
from ....core.interfaces.repositories.i_config_repository import (
    IConfigRepository,
)
from ....core.exceptions.revisao_exceptions import (
    ConvergenciaException,
)
from ....core.exceptions.agent_exceptions import (
    InvalidResponseException,
)
from .dto import RevisarSecaoOutputDTO

# Número padrão máximo de iterações
MAX_ITERACOES_PADRAO = 5
# Limiar de convergência padrão
LIMIAR_CONVERGENCIA_PADRAO = 0.95


class RevisarSecaoUseCase:
    """
    Caso de uso para revisão iterativa de uma seção.

    Coordena o processo de revisão enviando o conteúdo
    para agentes de IA e iterando até convergência.

    O processo é considerado convergido quando a
    diferença de erros entre iterações consecutivas
    cai abaixo do limiar configurado.

    Attributes:
        _agente: Agente de IA para revisão
        _config_repo: Repositório de configurações
        _logger: Sistema de logging
    """

    def __init__(
        self,
        agente: IAIAgent,
        config_repo: IConfigRepository,
        logger: ILogger,
    ) -> None:
        """
        Inicializa o caso de uso.

        Args:
            agente: Agente de IA para revisão
            config_repo: Repositório de configurações
            logger: Sistema de logging
        """
        self._agente = agente
        self._config_repo = config_repo
        self._logger = logger

    async def executar(
        self,
        secao: Secao,
        texto: TextoEstruturado,
        max_iteracoes: int = MAX_ITERACOES_PADRAO,
        limiar: float = LIMIAR_CONVERGENCIA_PADRAO,
    ) -> RevisarSecaoOutputDTO:
        """
        Executa a revisão iterativa da seção.

        Args:
            secao: Seção a ser revisada
            texto: Texto que contém a seção
            max_iteracoes: Máximo de iterações
            limiar: Limiar de convergência

        Returns:
            DTO com resultado da revisão

        Raises:
            ConvergenciaException: Se não convergir
        """
        self._logger.info(
            f"Iniciando revisão: {secao.titulo}"
        )
        secao.status = StatusTexto.REVISANDO

        # Carregar configuração da seção
        config = self._obter_configuracao(
            secao.configuracao_id
        )

        nome_agente = self._agente.obter_nome()
        texto_atual = secao.conteudo_original
        erros_anterior = 0
        convergiu = False

        for i in range(1, max_iteracoes + 1):
            self._logger.info(
                f"  [{nome_agente}] Iteração {i}/{max_iteracoes} "
                f"| Seção: '{secao.titulo}' "
                f"| Entrada: {len(texto_atual)} chars"
            )

            # Injetar texto atual na configuração
            config["texto_entrada"] = texto_atual

            # Executar revisão com agente
            try:
                inicio_ia = time.time()
                self._logger.info(
                    f"  [{nome_agente}] ⏳ Enviando à IA "
                    f"({len(texto_atual)} chars)..."
                )
                revisao = await self._agente.processar(
                    secao, config
                )
                tempo_ia = time.time() - inicio_ia
                self._logger.info(
                    f"  [{nome_agente}] ✅ Resposta da IA "
                    f"recebida em {tempo_ia:.1f}s"
                )
            except InvalidResponseException as e:
                self._logger.warning(
                    f"  [{nome_agente}] Iteração {i}: "
                    f"resposta inválida da IA (JSON truncado?). "
                    f"Tentando novamente... ({e})"
                )
                # Limpar cache para forçar nova requisição
                if hasattr(self._agente, '_gateway'):
                    self._agente._gateway.limpar_cache()
                continue

            revisao.numero_iteracao = i
            revisao.texto_entrada = texto_atual
            revisao.finalizar()

            # Registrar revisão na seção
            secao.adicionar_revisao(revisao)

            # Verificar convergência
            erros_atual = revisao.total_erros
            self._logger.info(
                f"  [{nome_agente}] Iteração {i} concluída: "
                f"{erros_atual} erro(s) "
                f"(anterior: {erros_anterior})"
            )
            convergiu = self._verificar_convergencia(
                erros_anterior, erros_atual, limiar
            )

            if convergiu:
                revisao.convergiu = True
                self._logger.info(
                    f"✓ Convergência atingida em "
                    f"{i} iteração(ões) para '{secao.titulo}'"
                )
                break

            # Atualizar para próxima iteração
            if revisao.texto_saida:
                texto_atual = revisao.texto_saida
            erros_anterior = erros_atual

        if not convergiu:
            self._logger.warning(
                f"✗ Não convergiu em {max_iteracoes} "
                f"iterações para '{secao.titulo}'"
            )

        secao.status = StatusTexto.CONCLUIDO

        return self._criar_output(secao, convergiu)

    def _obter_configuracao(
        self, config_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Obtém configuração para a seção.

        Args:
            config_id: ID da configuração

        Returns:
            Dicionário com configurações
        """
        if config_id:
            config = self._config_repo.carregar_prompt(
                config_id
            )
            if config:
                return config

        # Tentar carregar configuração global como fallback
        global_config = self._config_repo.carregar_configuracao()
        
        return {
            "tipo": "revisao_gramatical",
            "temperatura": global_config.get("temperatura_revisao", 0.3),
            "max_tokens": global_config.get("max_tokens_revisao", 4096),
        }

    def _verificar_convergencia(
        self,
        erros_anterior: int,
        erros_atual: int,
        limiar: float,
    ) -> bool:
        """
        Verifica se a revisão convergiu.

        Convergência é atingida quando novos erros
        são zero ou a redução proporcional é mínima.

        Args:
            erros_anterior: Erros na iteração anterior
            erros_atual: Erros na iteração atual
            limiar: Limiar de convergência

        Returns:
            True se convergiu
        """
        if erros_atual == 0:
            return True

        if erros_anterior == 0:
            return False

        taxa_reducao = 1.0 - (
            erros_atual / erros_anterior
        )
        return taxa_reducao < (1.0 - limiar)

    def _criar_output(
        self,
        secao: Secao,
        convergiu: bool,
    ) -> RevisarSecaoOutputDTO:
        """
        Cria DTO de saída com resultados.

        Args:
            secao: Seção revisada
            convergiu: Se convergiu

        Returns:
            DTO com resultados
        """
        erros = secao.obter_todos_erros()
        erros_por_tipo: Dict[str, int] = {}
        for erro in erros:
            tipo = erro.tipo.value
            erros_por_tipo[tipo] = (
                erros_por_tipo.get(tipo, 0) + 1
            )

        ultima = secao.obter_ultima_revisao()
        texto = (
            ultima.texto_saida if ultima else ""
        )

        return RevisarSecaoOutputDTO(
            titulo_secao=secao.titulo,
            total_erros=len(erros),
            total_iteracoes=secao.total_iteracoes,
            convergiu=convergiu,
            erros_por_tipo=erros_por_tipo,
            texto_revisado=texto,
            sucesso=True,
        )
