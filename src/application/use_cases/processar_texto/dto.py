"""
DTOs do caso de uso ProcessarTexto.

Define objetos de transferência de dados para entrada,
saída e progresso do processamento de textos.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from ....core.entities.texto_estruturado import TextoEstruturado


@dataclass
class ProcessarTextoInputDTO:
    """
    DTO de entrada para processamento de texto.

    Attributes:
        caminho_arquivo: Caminho do arquivo de texto
        formatos_relatorio: Formatos de saída desejados
        opcoes: Opções adicionais de processamento
    """

    caminho_arquivo: str
    formatos_relatorio: List[str] = field(
        default_factory=lambda: ["markdown"]
    )
    opcoes: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ProcessarTextoOutputDTO:
    """
    DTO de saída do processamento de texto.

    Attributes:
        texto: Texto processado
        relatorios: Caminhos dos relatórios gerados
        metricas: Métricas do processamento
        sucesso: Se o processamento foi bem-sucedido
        mensagem: Mensagem de resultado
    """

    texto: Optional[TextoEstruturado] = None
    relatorios: Dict[str, str] = field(
        default_factory=dict
    )
    metricas: Dict[str, Any] = field(
        default_factory=dict
    )
    sucesso: bool = True
    mensagem: str = ""


@dataclass
class ProgressoDTO:
    """
    DTO para notificação de progresso.

    Attributes:
        etapa: Nome da etapa atual
        percentual: Percentual de conclusão (0-100)
        mensagem: Mensagem descritiva do progresso
        detalhes: Detalhes adicionais
    """

    etapa: str
    percentual: float
    mensagem: str
    detalhes: Dict[str, Any] = field(
        default_factory=dict
    )
