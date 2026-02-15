"""
Caso de uso: Gerar Relatório.

Orquestra a geração de relatórios de revisão
em diferentes formatos de saída.
"""

from pathlib import Path
from typing import Dict, Any

from ....core.entities.texto_estruturado import TextoEstruturado
from ....core.entities.relatorio import Relatorio
from ....core.enums.formato_relatorio import (
    FormatoRelatorio,
)
from ....core.interfaces.services.i_report_generator import (
    IReportGenerator,
)
from ....core.interfaces.services.i_logger import (
    ILogger,
)
from .dto import (
    GerarRelatorioInputDTO,
    GerarRelatorioOutputDTO,
)


class GerarRelatorioUseCase:
    """
    Caso de uso para geração de relatórios.

    Coordena a geração de relatórios de revisão
    usando o gerador apropriado para o formato.

    Attributes:
        _geradores: Mapa de geradores por formato
        _logger: Sistema de logging
    """

    def __init__(
        self,
        geradores: Dict[str, IReportGenerator],
        logger: ILogger,
    ) -> None:
        """
        Inicializa o caso de uso.

        Args:
            geradores: Geradores indexados por formato
            logger: Sistema de logging
        """
        self._geradores = geradores
        self._logger = logger

    async def executar(
        self,
        texto: TextoEstruturado,
        formato: str,
        diretorio_saida: str = "./output",
    ) -> str:
        """
        Gera relatório no formato especificado.

        Args:
            texto: Texto processado
            formato: Formato desejado
            diretorio_saida: Diretório de saída

        Returns:
            Caminho do arquivo gerado

        Raises:
            ValueError: Se formato não suportado
        """
        self._logger.info(
            f"Gerando relatório {formato} para "
            f"'{texto.nome_arquivo}'"
        )

        gerador = self._geradores.get(formato)
        if not gerador:
            formatos = list(self._geradores.keys())
            raise ValueError(
                f"Formato '{formato}' não suportado. "
                f"Disponíveis: {formatos}"
            )

        # Garantir que diretório existe
        Path(diretorio_saida).mkdir(
            parents=True, exist_ok=True
        )

        # Gerar relatório
        relatorio = gerador.gerar(texto)

        # Salvar no diretório
        caminho = gerador.salvar(
            relatorio, diretorio_saida
        )

        self._logger.info(
            f"Relatório salvo em: {caminho}"
        )

        return caminho
