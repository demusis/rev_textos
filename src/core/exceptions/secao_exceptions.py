"""
Exceções relacionadas à entidade Seção.

Define exceções específicas para erros envolvendo
operações com seções de textos.
"""

from .base_exception import RevisorTextosException


class SecaoException(RevisorTextosException):
    """Exceção base para erros relacionados a seções."""

    pass


class SecaoInvalidaException(SecaoException):
    """
    Exceção para seção com dados inválidos.

    Lançada quando uma seção não passa nas validações
    de conteúdo, paginação ou estrutura.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem, codigo="SECAO_INVALIDA")


class RevisaoNaoEncontradaException(SecaoException):
    """
    Exceção para revisão não encontrada em uma seção.

    Lançada quando se busca uma revisão por índice
    ou identificador inexistente.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(
            mensagem, codigo="REVISAO_NAO_ENCONTRADA"
        )
