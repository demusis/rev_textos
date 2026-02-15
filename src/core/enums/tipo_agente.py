"""
Módulo de enumeração de tipos de agente de IA.

Define os diferentes agentes especializados que participam
do processo de revisão de textos.
"""

from enum import Enum


class TipoAgente(Enum):
    """
    Enumeração dos tipos de agentes de IA disponíveis.

    Cada agente tem uma especialização diferente no processo
    de revisão do texto estruturado.

    Attributes:
        REVISOR: Agente principal de revisão de conteúdo
        VALIDADOR: Agente de validação de correções
        CONSISTENCIA: Agente de verificação de consistência
        SINTESE: Agente de geração de síntese final
    """

    REVISOR = "revisor"
    VALIDADOR = "validador"
    CONSISTENCIA = "consistencia"
    SINTESE = "sintese"

    def __str__(self) -> str:
        """Retorna representação legível do tipo."""
        return self.value
