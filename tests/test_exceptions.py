"""Testes das exceções do domínio."""

import pytest
from src.core.exceptions.base_exception import (
    RevisorTextosException,
)
from src.core.exceptions.texto_exceptions import (
    TextoException,
    TextoInvalidoException,
    TextoNaoEncontradoException,
)
from src.core.exceptions.pdf_exceptions import (
    PDFException,
    PDFInvalidoException,
    PDFProtegidoException,
    ExtracaoException,
)
from src.core.exceptions.agent_exceptions import (
    AgentException,
    APIException,
    TimeoutException,
    RateLimitException,
)


class TestHierarquiaExcecoes:
    """Testa hierarquia de exceções."""

    def test_base_exception(self):
        e = RevisorTextosException("teste")
        assert str(e) is not None
        assert isinstance(e, Exception)

    def test_texto_exceptions_herdam_base(self):
        e = TextoInvalidoException("x")
        assert isinstance(e, TextoException)
        assert isinstance(e, RevisorTextosException)

    def test_pdf_exceptions_herdam_base(self):
        e = PDFProtegidoException("x")
        assert isinstance(e, PDFException)
        assert isinstance(e, RevisorTextosException)

    def test_agent_exceptions_herdam_base(self):
        e = APIException("x")
        assert isinstance(e, AgentException)
        assert isinstance(e, RevisorTextosException)

    def test_codigo_erro(self):
        e = TextoInvalidoException("teste")
        assert e.codigo is not None

    def test_timeout_exception(self):
        e = TimeoutException("timeout")
        assert isinstance(e, AgentException)

    def test_rate_limit_exception(self):
        e = RateLimitException("limit")
        assert isinstance(e, AgentException)

    def test_extracao_exception(self):
        e = ExtracaoException("falha extração")
        assert isinstance(e, PDFException)
