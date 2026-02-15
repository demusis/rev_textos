"""
Módulo contendo a entidade Correção.

Define a estrutura de uma correção proposta para
um erro identificado no texto estruturado.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Correcao:
    """
    Representa uma correção proposta para um erro.

    Contém o texto original, o texto corrigido e
    metadados sobre a origem e qualidade da correção.

    Attributes:
        texto_original: Trecho original com erro
        texto_corrigido: Texto corrigido proposto
        justificativa: Explicação da correção
        agente_origem: Agente que propôs a correção
        confianca: Grau de confiança (0.0-1.0)
        aplicada: Se a correção foi aplicada
        data_proposta: Data/hora da proposta
        iteracao: Número da iteração em que foi proposta

    Example:
        >>> correcao = Correcao(
        ...     texto_original="os dados foi analisados",
        ...     texto_corrigido="os dados foram analisados",
        ...     justificativa="Concordância verbal",
        ...     agente_origem="revisor"
        ... )
    """

    texto_original: str
    texto_corrigido: str
    justificativa: str = ""
    agente_origem: str = ""
    confianca: float = 1.0
    aplicada: bool = False
    data_proposta: datetime = field(
        default_factory=datetime.now
    )
    iteracao: int = 0

    def aplicar(self) -> None:
        """Marca a correção como aplicada."""
        self.aplicada = True

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário."""
        return {
            "texto_original": self.texto_original,
            "texto_corrigido": self.texto_corrigido,
            "justificativa": self.justificativa,
            "agente_origem": self.agente_origem,
            "confianca": self.confianca,
            "aplicada": self.aplicada,
            "data_proposta": (
                self.data_proposta.isoformat()
            ),
            "iteracao": self.iteracao,
        }

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any]
    ) -> "Correcao":
        """
        Cria instância a partir de dicionário.

        Args:
            data: Dicionário com dados da correção

        Returns:
            Nova instância de Correcao
        """
        return cls(
            texto_original=data["texto_original"],
            texto_corrigido=data["texto_corrigido"],
            justificativa=data.get("justificativa", ""),
            agente_origem=data.get("agente_origem", ""),
            confianca=data.get("confianca", 1.0),
            aplicada=data.get("aplicada", False),
            iteracao=data.get("iteracao", 0),
        )

    def __str__(self) -> str:
        """Representação legível."""
        status = "aplicada" if self.aplicada else "pendente"
        return (
            f"Correção({status}: "
            f"'{self.texto_original[:30]}' → "
            f"'{self.texto_corrigido[:30]}')"
        )
