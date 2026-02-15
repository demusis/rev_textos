"""
DTOs do caso de uso GerarRelatorio.

Define objetos de transferência de dados para
a geração de relatórios de revisão.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class GerarRelatorioInputDTO:
    """
    DTO de entrada para geração de relatório.

    Attributes:
        formato: Formato de saída desejado
        diretorio_saida: Diretório para salvar
        incluir_detalhes: Se inclui detalhes completos
        incluir_metricas: Se inclui métricas
    """

    formato: str = "markdown"
    diretorio_saida: str = "./output"
    incluir_detalhes: bool = True
    incluir_metricas: bool = True


@dataclass
class GerarRelatorioOutputDTO:
    """
    DTO de saída da geração de relatório.

    Attributes:
        caminho_arquivo: Caminho do arquivo gerado
        formato: Formato do relatório
        tamanho_bytes: Tamanho do arquivo
        sucesso: Se geração foi bem-sucedida
        mensagem: Mensagem de resultado
    """

    caminho_arquivo: str = ""
    formato: str = ""
    tamanho_bytes: int = 0
    sucesso: bool = True
    mensagem: str = ""
