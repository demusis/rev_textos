"""
Exceções relacionadas à entidade Texto Estruturado.

Define exceções específicas para erros envolvendo
operações com textos estruturados.
"""

from .base_exception import RevisorTextosException


class TextoException(RevisorTextosException):
    """Exceção base para erros relacionados a textos."""

    pass


class TextoInvalidoException(TextoException):
    """
    Exceção para texto com dados inválidos.

    Lançada quando um texto não passa nas validações
    de integridade, formato ou conteúdo.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem, codigo="TEXTO_INVALIDO")


class TextoNaoEncontradoException(TextoException):
    """
    Exceção para texto não encontrado.

    Lançada quando o arquivo do texto não é
    encontrado no caminho especificado.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem, codigo="TEXTO_NAO_ENCONTRADO")


class SecaoNaoEncontradaException(TextoException):
    """
    Exceção para seção não encontrada em um texto.

    Lançada quando uma busca por seção não retorna
    resultados no texto especificado.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem, codigo="SECAO_NAO_ENCONTRADA")


class SecaoDuplicadaException(TextoException):
    """
    Exceção para tentativa de adicionar seção duplicada.

    Lançada quando se tenta adicionar uma seção com
    título já existente no texto.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem, codigo="SECAO_DUPLICADA")
