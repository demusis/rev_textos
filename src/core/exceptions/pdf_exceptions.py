"""
Exceções relacionadas ao processamento de PDF.

Define exceções específicas para erros durante
a leitura, extração e validação de arquivos PDF.
"""

from .base_exception import RevisorTextosException


class PDFException(RevisorTextosException):
    """Exceção base para erros de PDF."""

    pass


class PDFInvalidoException(PDFException):
    """
    Exceção para PDF inválido ou corrompido.

    Lançada quando o arquivo PDF não pode ser lido,
    está corrompido ou não é um PDF válido.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem, codigo="PDF_INVALIDO")


class PDFProtegidoException(PDFException):
    """
    Exceção para PDF protegido por senha.

    Lançada quando o PDF requer senha para leitura
    e a senha não foi fornecida.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem, codigo="PDF_PROTEGIDO")


class ExtracaoException(PDFException):
    """
    Exceção para falha na extração de conteúdo.

    Lançada quando a extração de texto ou imagens
    falha de forma irrecuperável.
    """

    def __init__(self, mensagem: str) -> None:
        super().__init__(
            mensagem, codigo="EXTRACAO_FALHOU"
        )
