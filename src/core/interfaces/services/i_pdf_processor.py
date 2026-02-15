"""
Interface do processador de PDF.

Define o contrato para extração de texto, metadados
e detecção de seções em arquivos PDF.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from ...value_objects.metadados_pdf import MetadadosPDF


@dataclass
class SecaoDetectada:
    """
    Resultado da detecção de uma seção no PDF.

    Attributes:
        titulo: Título da seção detectada
        conteudo: Conteúdo textual da seção
        pagina_inicio: Página inicial
        pagina_fim: Página final
        nivel: Nível hierárquico
    """

    titulo: str
    conteudo: str
    pagina_inicio: int
    pagina_fim: int
    nivel: int = 1


class IPdfProcessor(ABC):
    """
    Interface para processamento de PDF.

    Define operações de validação, extração de texto,
    metadados e detecção de seções.
    """

    @abstractmethod
    async def validar_pdf(
        self, caminho: str
    ) -> bool:
        """
        Valida se o arquivo é um PDF válido.

        Args:
            caminho: Caminho do arquivo PDF

        Returns:
            True se válido, False caso contrário
        """

    @abstractmethod
    async def extrair_texto(
        self, caminho: str
    ) -> str:
        """
        Extrai texto completo do PDF.

        Args:
            caminho: Caminho do arquivo PDF

        Returns:
            Texto completo extraído
        """

    @abstractmethod
    async def extrair_metadados(
        self, caminho: str
    ) -> MetadadosPDF:
        """
        Extrai metadados do PDF.

        Args:
            caminho: Caminho do arquivo PDF

        Returns:
            Objeto MetadadosPDF preenchido
        """

    @abstractmethod
    async def detectar_secoes(
        self,
        texto: str,
        numero_paginas: int = 0,
    ) -> List[SecaoDetectada]:
        """
        Detecta seções no texto extraído.

        Args:
            texto: Texto completo do PDF
            numero_paginas: Total de páginas

        Returns:
            Lista de seções detectadas
        """

    @abstractmethod
    async def extrair_texto_por_pagina(
        self, caminho: str, pagina: int
    ) -> str:
        """
        Extrai texto de uma página específica.

        Args:
            caminho: Caminho do PDF
            pagina: Número da página (base 1)

        Returns:
            Texto da página
        """
