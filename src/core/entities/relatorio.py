"""
Módulo contendo a entidade Relatório.

Define a estrutura do relatório de revisão gerado
após processamento completo do texto.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..enums.formato_relatorio import FormatoRelatorio


@dataclass
class Relatorio:
    """
    Representa um relatório de revisão gerado.

    Contém os resultados do processamento, formato
    de saída e caminho do arquivo gerado.

    Attributes:
        titulo: Título do relatório
        formato: Formato de saída do relatório
        conteudo: Conteúdo do relatório (texto/markup)
        caminho_arquivo: Caminho do arquivo gerado
        data_geracao: Data/hora da geração
        texto_nome: Nome do documento de origem
        total_secoes: Total de seções analisadas
        total_erros: Total de erros encontrados
        resumo: Resumo executivo do relatório
        metadados: Metadados adicionais
    """

    titulo: str
    formato: FormatoRelatorio
    conteudo: str = ""
    caminho_arquivo: Optional[str] = None
    data_geracao: datetime = field(
        default_factory=datetime.now
    )
    texto_nome: str = ""
    total_secoes: int = 0
    total_erros: int = 0
    resumo: str = ""
    metadados: Dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def esta_salvo(self) -> bool:
        """Verifica se o relatório foi salvo."""
        return self.caminho_arquivo is not None

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário."""
        return {
            "titulo": self.titulo,
            "formato": self.formato.value,
            "caminho_arquivo": self.caminho_arquivo,
            "data_geracao": (
                self.data_geracao.isoformat()
            ),
            "texto_nome": self.texto_nome,
            "total_secoes": self.total_secoes,
            "total_erros": self.total_erros,
            "resumo": self.resumo,
            "metadados": self.metadados,
        }

    def __str__(self) -> str:
        """Representação legível."""
        return (
            f"Relatório({self.titulo}, "
            f"{self.formato.value})"
        )
