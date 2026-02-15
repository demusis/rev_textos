"""
Módulo de enumeração de formatos de relatório.

Define os formatos de saída suportados para geração
de relatórios de revisão.
"""

from enum import Enum


class FormatoRelatorio(Enum):
    """
    Enumeração dos formatos de relatório suportados.

    Attributes:
        MARKDOWN: Formato Markdown (.md)
        HTML: Formato HTML (.html)
        PDF: Formato PDF (.pdf)
        DOCX: Formato Word (.docx)
        LATEX: Formato LaTeX (.tex)
    """

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"
    LATEX = "latex"

    def __str__(self) -> str:
        """Retorna representação legível do formato."""
        return self.value

    @property
    def extensao(self) -> str:
        """Retorna a extensão de arquivo correspondente."""
        extensoes = {
            FormatoRelatorio.MARKDOWN: ".md",
            FormatoRelatorio.HTML: ".html",
            FormatoRelatorio.PDF: ".pdf",
            FormatoRelatorio.DOCX: ".docx",
            FormatoRelatorio.LATEX: ".tex",
        }
        return extensoes[self]
