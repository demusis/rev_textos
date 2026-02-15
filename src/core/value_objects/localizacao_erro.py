"""
Módulo do Value Object LocalizacaoErro.

Define a localização precisa de um erro identificado
dentro do texto estruturado, incluindo página e posição.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LocalizacaoErro:
    """
    Localização de um erro no texto estruturado.

    Objeto de valor imutável que identifica com precisão
    onde um erro foi encontrado no documento original.

    Attributes:
        pagina: Número da página onde o erro foi encontrado
        paragrafo: Número do parágrafo dentro da página
        linha: Número da linha dentro do parágrafo
        posicao_inicio: Posição inicial do trecho com erro
        posicao_fim: Posição final do trecho com erro
        contexto: Trecho de texto ao redor do erro

    Example:
        >>> loc = LocalizacaoErro(
        ...     pagina=5,
        ...     paragrafo=3,
        ...     linha=2,
        ...     posicao_inicio=45,
        ...     posicao_fim=60,
        ...     contexto="...texto ao redor do erro..."
        ... )
    """

    pagina: int
    paragrafo: int = 0
    linha: int = 0
    posicao_inicio: int = 0
    posicao_fim: int = 0
    contexto: Optional[str] = None

    def __post_init__(self) -> None:
        """Valida os dados da localização."""
        if self.pagina < 1:
            raise ValueError(
                "Número da página deve ser >= 1"
            )
        if self.posicao_fim < self.posicao_inicio:
            raise ValueError(
                "Posição final deve ser >= posição inicial"
            )

    def to_dict(self) -> dict:
        """Serializa para dicionário."""
        return {
            "pagina": self.pagina,
            "paragrafo": self.paragrafo,
            "linha": self.linha,
            "posicao_inicio": self.posicao_inicio,
            "posicao_fim": self.posicao_fim,
            "contexto": self.contexto,
        }

    def __str__(self) -> str:
        """Representação legível."""
        return (
            f"Página {self.pagina}, "
            f"parágrafo {self.paragrafo}, "
            f"linha {self.linha}"
        )
