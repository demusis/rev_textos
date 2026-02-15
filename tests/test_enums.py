"""Testes dos enums do domínio."""

import pytest
from src.core.enums.status_texto import StatusTexto
from src.core.enums.tipo_erro import TipoErro
from src.core.enums.tipo_agente import TipoAgente
from src.core.enums.formato_relatorio import (
    FormatoRelatorio,
)


class TestStatusTexto:
    """Testes para enum StatusTexto."""

    def test_valores_existem(self):
        assert StatusTexto.PENDENTE
        assert StatusTexto.PROCESSANDO
        assert StatusTexto.CONCLUIDO
        assert StatusTexto.ERRO

    def test_estados_finalizados(self):
        assert StatusTexto.CONCLUIDO.esta_finalizado
        assert StatusTexto.ERRO.esta_finalizado
        assert not StatusTexto.PENDENTE.esta_finalizado
        assert not StatusTexto.PROCESSANDO.esta_finalizado

    def test_estados_ativos(self):
        assert StatusTexto.PROCESSANDO.esta_ativo
        assert not StatusTexto.CONCLUIDO.esta_ativo

    def test_valor_string(self):
        assert isinstance(
            StatusTexto.PENDENTE.value, str
        )


class TestTipoErro:
    """Testes para enum TipoErro."""

    def test_tipos_existem(self):
        assert TipoErro.GRAMATICAL
        assert TipoErro.TECNICO
        assert TipoErro.CONSISTENCIA
        assert TipoErro.FORMATACAO
        assert TipoErro.TECNICO  # Anteriormente JURIDICO, agora mapeado para TECNICO

    def test_todos_tem_valor(self):
        for tipo in TipoErro:
            assert tipo.value
            assert len(tipo.value) > 2


class TestTipoAgente:
    """Testes para enum TipoAgente."""

    def test_agentes_existem(self):
        assert TipoAgente.REVISOR
        assert TipoAgente.VALIDADOR
        assert TipoAgente.CONSISTENCIA


class TestFormatoRelatorio:
    """Testes para enum FormatoRelatorio."""

    def test_formatos_existem(self):
        assert FormatoRelatorio.MARKDOWN
        assert FormatoRelatorio.HTML

    def test_extensoes(self):
        assert FormatoRelatorio.MARKDOWN.extensao == ".md"
        assert FormatoRelatorio.HTML.extensao == ".html"
