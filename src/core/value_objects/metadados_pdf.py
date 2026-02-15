"""
Módulo do Value Object MetadadosPDF.

Define os metadados extraídos de um arquivo PDF,
como autor, título, datas e informações do produtor.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class MetadadosPDF:
    """
    Metadados extraídos de um arquivo PDF.

    Objeto de valor imutável contendo informações sobre
    a origem e propriedades do documento PDF.

    Attributes:
        numero_paginas: Total de páginas do documento
        titulo: Título do documento (metadado PDF)
        autor: Autor do documento (metadado PDF)
        criador: Software criador do PDF
        produtor: Software produtor do PDF
        data_criacao: Data de criação do PDF
        data_modificacao: Data da última modificação
        tamanho_bytes: Tamanho do arquivo em bytes
        versao_pdf: Versão do formato PDF
        criptografado: Se o PDF é criptografado
        contem_imagens: Se o PDF contém imagens
        contem_tabelas: Se o PDF contém tabelas

    Example:
        >>> meta = MetadadosPDF(
        ...     numero_paginas=45,
        ...     titulo="Texto Estruturado 001/2024",
        ...     autor="Perito João"
        ... )
    """

    numero_paginas: int
    titulo: Optional[str] = None
    autor: Optional[str] = None
    criador: Optional[str] = None
    produtor: Optional[str] = None
    data_criacao: Optional[datetime] = None
    data_modificacao: Optional[datetime] = None
    tamanho_bytes: int = 0
    versao_pdf: Optional[str] = None
    criptografado: bool = False
    contem_imagens: bool = False
    contem_tabelas: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário."""
        return {
            "numero_paginas": self.numero_paginas,
            "titulo": self.titulo,
            "autor": self.autor,
            "criador": self.criador,
            "produtor": self.produtor,
            "data_criacao": (
                self.data_criacao.isoformat()
                if self.data_criacao
                else None
            ),
            "data_modificacao": (
                self.data_modificacao.isoformat()
                if self.data_modificacao
                else None
            ),
            "tamanho_bytes": self.tamanho_bytes,
            "versao_pdf": self.versao_pdf,
            "criptografado": self.criptografado,
            "contem_imagens": self.contem_imagens,
            "contem_tabelas": self.contem_tabelas,
        }

    def __str__(self) -> str:
        """Representação legível."""
        return (
            f"PDF: {self.titulo or 'Sem título'} "
            f"({self.numero_paginas} páginas)"
        )
