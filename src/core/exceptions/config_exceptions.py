"""
Exceções relacionadas a configurações.

Define exceções específicas para erros de validação,
carregamento e persistência de configurações.
"""

from .base_exception import RevisorTextosException


class ConfigException(RevisorTextosException):
    """Exceção base para erros de configuração."""

    pass


class ConfiguracaoInvalidaException(ConfigException):
    """
    Exceção para configuração inválida.

    Lançada quando uma configuração não passa na
    validação de schema ou contém valores inválidos.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(
            mensagem, codigo="CONFIG_INVALIDA"
        )


class ConfiguracaoNaoEncontradaException(ConfigException):
    """
    Exceção para configuração não encontrada.

    Lançada quando o arquivo ou chave de configuração
    solicitada não existe.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(
            mensagem, codigo="CONFIG_NAO_ENCONTRADA"
        )
