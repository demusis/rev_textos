"""
Exceções relacionadas ao processo de revisão.

Define exceções específicas para erros durante
o processo de revisão por agentes de IA.
"""

from .base_exception import RevisorTextosException


class RevisaoException(RevisorTextosException):
    """Exceção base para erros de revisão."""

    pass


class ConvergenciaException(RevisaoException):
    """
    Exceção para falha na convergência da revisão.

    Lançada quando o processo iterativo de revisão
    não converge dentro do limite de iterações.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(
            mensagem, codigo="CONVERGENCIA_FALHOU"
        )


class RevisaoInvalidaException(RevisaoException):
    """
    Exceção para revisão com dados inválidos.

    Lançada quando uma revisão contém dados inconsistentes
    ou incompletos.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(
            mensagem, codigo="REVISAO_INVALIDA"
        )
