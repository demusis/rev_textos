"""
Caso de uso: Verificar Consistência.

Verifica a consistência entre seções do texto,
identificando contradições e divergências.
"""

from typing import Dict, Any, List

from ....core.entities.texto_estruturado import TextoEstruturado
from ....core.interfaces.services.i_ai_agent import (
    IAIAgent,
)
from ....core.interfaces.services.i_logger import (
    ILogger,
)


class VerificarConsistenciaUseCase:
    """
    Caso de uso para verificação de consistência.

    Analisa todas as seções revisadas em conjunto
    para identificar inconsistências entre elas.

    Attributes:
        _agente: Agente de consistência
        _logger: Sistema de logging
    """

    def __init__(
        self,
        agente: IAIAgent,
        logger: ILogger,
    ) -> None:
        """
        Inicializa o caso de uso.

        Args:
            agente: Agente de consistência
            logger: Sistema de logging
        """
        self._agente = agente
        self._logger = logger

    async def executar(
        self, texto: TextoEstruturado
    ) -> Dict[str, Any]:
        """
        Verifica consistência entre seções.

        Args:
            texto: Texto com seções revisadas

        Returns:
            Dicionário com resultados da verificação
        """
        self._logger.info(
            "Verificando consistência entre seções"
        )

        # Preparar contexto com todas as seções
        contexto = self._preparar_contexto(texto)

        # Enviar para agente de consistência
        resultado = await self._agente.gerar_sintese(
            contexto
        )

        self._logger.info(
            "Verificação de consistência concluída"
        )

        return {
            "resultado": resultado,
            "total_secoes_analisadas": len(
                texto.secoes
            ),
        }

    def _preparar_contexto(
        self, texto: TextoEstruturado
    ) -> Dict[str, Any]:
        """
        Prepara contexto com dados das seções.

        Args:
            texto: Texto fonte

        Returns:
            Contexto estruturado
        """
        secoes_resumo: List[Dict[str, Any]] = []

        for secao in texto.secoes:
            ultima = secao.obter_ultima_revisao()
            conteudo_secao = (
                ultima.texto_saida
                if ultima and ultima.texto_saida
                else secao.conteudo_original
            )
            secoes_resumo.append(
                {
                    "titulo": secao.titulo,
                    "conteudo": conteudo_secao[:5000],
                    "erros": len(
                        secao.obter_todos_erros()
                    ),
                }
            )

        return {
            "texto_nome": texto.nome_arquivo,
            "secoes": secoes_resumo,
        }
