"""
Módulo do Value Object MetricasRevisao.

Define as métricas coletadas durante o processo
de revisão de uma seção ou texto completo.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class MetricasRevisao:
    """
    Métricas coletadas durante o processo de revisão.

    Objeto de valor imutável contendo estatísticas
    do processamento realizado pelos agentes de IA.

    Attributes:
        total_iteracoes: Número de iterações de revisão
        total_erros: Total de erros encontrados
        erros_por_tipo: Distribuição de erros por tipo
        tokens_consumidos: Total de tokens usados na API
        tempo_processamento_seg: Tempo total em segundos
        convergiu: Se o processo convergiu naturalmente
        custo_estimado_usd: Custo estimado em dólares

    Example:
        >>> metricas = MetricasRevisao(
        ...     total_iteracoes=3,
        ...     total_erros=12,
        ...     tokens_consumidos=8500,
        ...     tempo_processamento_seg=45.2,
        ...     convergiu=True
        ... )
    """

    total_iteracoes: int = 0
    total_erros: int = 0
    erros_por_tipo: Dict[str, int] = None  # type: ignore
    tokens_consumidos: int = 0
    tempo_processamento_seg: float = 0.0
    convergiu: bool = False
    custo_estimado_usd: float = 0.0

    def __post_init__(self) -> None:
        """Inicializa valores default para campos mutáveis."""
        if self.erros_por_tipo is None:
            # Workaround para frozen dataclass com dict
            object.__setattr__(
                self, "erros_por_tipo", {}
            )

    def to_dict(self) -> dict:
        """Serializa para dicionário."""
        return {
            "total_iteracoes": self.total_iteracoes,
            "total_erros": self.total_erros,
            "erros_por_tipo": dict(self.erros_por_tipo),
            "tokens_consumidos": self.tokens_consumidos,
            "tempo_processamento_seg": (
                self.tempo_processamento_seg
            ),
            "convergiu": self.convergiu,
            "custo_estimado_usd": self.custo_estimado_usd,
        }

    @property
    def custo_por_erro(self) -> float:
        """Calcula custo médio por erro encontrado."""
        if self.total_erros == 0:
            return 0.0
        return self.custo_estimado_usd / self.total_erros

    def __str__(self) -> str:
        """Representação legível."""
        return (
            f"Métricas: {self.total_erros} erros em "
            f"{self.total_iteracoes} iterações "
            f"({self.tempo_processamento_seg:.1f}s)"
        )
