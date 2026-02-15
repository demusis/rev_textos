"""
Caso de uso: Validar Revisão.

Valida os resultados de uma revisão usando um
agente validador independente.
"""

from typing import Dict, Any

from ....core.entities.secao import Secao
from ....core.entities.revisao import Revisao
from ....core.interfaces.services.i_ai_agent import (
    IAIAgent,
)
from ....core.interfaces.services.i_logger import (
    ILogger,
)


class ValidarRevisaoUseCase:
    """
    Caso de uso para validação de revisões.

    Utiliza um agente validador para confirmar
    que as correções propostas são adequadas.

    Attributes:
        _agente_validador: Agente de validação
        _logger: Sistema de logging
    """

    def __init__(
        self,
        agente_validador: IAIAgent,
        logger: ILogger,
    ) -> None:
        """
        Inicializa o caso de uso.

        Args:
            agente_validador: Agente validador
            logger: Sistema de logging
        """
        self._agente_validador = agente_validador
        self._logger = logger

    async def executar(
        self,
        secao: Secao,
        revisao: Revisao,
    ) -> Dict[str, Any]:
        """
        Valida os resultados de uma revisão.

        Args:
            secao: Seção original
            revisao: Revisão a ser validada

        Returns:
            Dicionário com resultado da validação
        """
        self._logger.info(
            f"Validando revisão da seção "
            f"'{secao.titulo}'"
        )

        config = {
            "tipo": "validacao",
            "texto_original": secao.conteudo_original,
            "texto_revisado": revisao.texto_saida,
            "erros_encontrados": [
                e.to_dict() for e in revisao.erros
            ],
        }

        resultado = (
            await self._agente_validador.processar(
                secao, config
            )
        )

        self._logger.info(
            f"Validação concluída: "
            f"{resultado.total_erros} problemas"
        )

        return {
            "validacao_ok": resultado.total_erros == 0,
            "problemas": resultado.total_erros,
            "detalhes": resultado.to_dict(),
        }
