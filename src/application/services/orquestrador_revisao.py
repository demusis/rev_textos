"""
Serviço de aplicação: Orquestrador de Revisão.

Serviço de alto nível que expõe operações
simplificadas para a camada de apresentação.
"""

from typing import Callable, Optional, Dict, Any, List

from ...core.interfaces.services.i_pdf_processor import (
    IPdfProcessor,
)
from ...core.interfaces.services.i_ai_agent import (
    IAIAgent,
)
from ...core.interfaces.services.i_report_generator import (
    IReportGenerator,
)
from ...core.interfaces.services.i_logger import (
    ILogger,
)
from ...core.interfaces.repositories.i_texto_repository import (
    ITextoRepository,
)
from ...core.interfaces.repositories.i_config_repository import (
    IConfigRepository,
)
from ..use_cases.processar_texto.processar_texto_use_case import (
    ProcessarTextoUseCase,
)
from ..use_cases.processar_texto.dto import (
    ProcessarTextoInputDTO,
    ProcessarTextoOutputDTO,
    ProgressoDTO,
)


class OrquestradorRevisao:
    """
    Serviço de aplicação para orquestração de revisões.

    Fachada simplificada que compõe use cases e expõe
    operações de alto nível para a GUI.

    Attributes:
        _logger: Sistema de logging
    """

    def __init__(
        self,
        pdf_processor: IPdfProcessor,
        agentes_revisores: List[IAIAgent],
        agente_validador: Optional[IAIAgent],
        agente_consistencia: Optional[IAIAgent],
        texto_repo: ITextoRepository,
        config_repo: IConfigRepository,
        geradores_relatorio: Dict[
            str, IReportGenerator
        ],
        logger: ILogger,
    ) -> None:
        """
        Inicializa o orquestrador.

        Args:
            pdf_processor: Processador de documento
            agentes_revisores: Lista de agentes revisores
            agente_validador: Agente de validação
            agente_consistencia: Agente de consistência
            texto_repo: Repositório de textos
            config_repo: Repositório de configurações
            geradores_relatorio: Geradores de relatório
            logger: Sistema de logging
        """
        self._logger = logger
        self._pdf_processor = pdf_processor
        self._agentes_revisores = agentes_revisores
        self._agente_validador = agente_validador
        self._agente_consistencia = (
            agente_consistencia
        )
        self._texto_repo = texto_repo
        self._config_repo = config_repo
        self._geradores_relatorio = (
            geradores_relatorio
        )

    async def processar_texto(
        self,
        caminho_arquivo: str,
        formatos: Optional[list] = None,
        callback_progresso: Optional[
            Callable[[ProgressoDTO], None]
        ] = None,
        check_cancel: Optional[Callable[[], None]] = None,
    ) -> ProcessarTextoOutputDTO:
        """
        Processa um texto estruturado completo.

        Método principal exposto para a GUI.

        Args:
            caminho_arquivo: Caminho do arquivo
            formatos: Formatos de relatório desejados
            callback_progresso: Callback para progresso
            check_cancel: Callback para verificar cancelamento

        Returns:
            DTO com resultado do processamento
        """
        if formatos is None:
            formatos = ["markdown"]

        use_case = ProcessarTextoUseCase(
            pdf_processor=self._pdf_processor,
            agentes_revisores=self._agentes_revisores,
            agente_validador=self._agente_validador,
            agente_consistencia=(
                self._agente_consistencia
            ),
            texto_repo=self._texto_repo,
            config_repo=self._config_repo,
            geradores_relatorio=(
                self._geradores_relatorio
            ),
            logger=self._logger,
            callback_progresso=callback_progresso,
            check_cancel=check_cancel,
        )

        input_dto = ProcessarTextoInputDTO(
            caminho_arquivo=caminho_arquivo,
            formatos_relatorio=formatos,
        )

        return await use_case.executar(input_dto)
