"""Testes dos value objects do domínio."""

import pytest
from src.core.value_objects.localizacao_erro import (
    LocalizacaoErro,
)
from src.core.value_objects.metadados_pdf import (
    MetadadosPDF,
)
from src.core.value_objects.metricas_revisao import (
    MetricasRevisao,
)


class TestLocalizacaoErro:
    """Testes para LocalizacaoErro."""

    def test_criacao_basica(self):
        loc = LocalizacaoErro(
            pagina=1,
            paragrafo=2,
            posicao_inicio=10,
            posicao_fim=20,
        )
        assert loc.pagina == 1
        assert loc.paragrafo == 2
        assert loc.posicao_inicio == 10

    def test_imutabilidade(self):
        loc = LocalizacaoErro(pagina=1)
        with pytest.raises(AttributeError):
            loc.pagina = 2  # type: ignore

    def test_to_dict(self):
        loc = LocalizacaoErro(
            pagina=3,
            linha=5,
            posicao_inicio=0,
            posicao_fim=10,
        )
        d = loc.to_dict()
        assert d["pagina"] == 3
        assert d["linha"] == 5

    def test_posicao_fim_invalida(self):
        with pytest.raises(ValueError):
            LocalizacaoErro(
                pagina=1,
                posicao_inicio=20,
                posicao_fim=10,
            )


class TestMetadadosPDF:
    """Testes para MetadadosPDF."""

    def test_criacao_minima(self):
        m = MetadadosPDF(numero_paginas=10)
        assert m.numero_paginas == 10
        assert m.titulo is None

    def test_criacao_completa(self):
        m = MetadadosPDF(
            numero_paginas=5,
            titulo="Texto",
            autor="Perito",
            tamanho_bytes=50000,
        )
        assert m.titulo == "Texto"
        assert m.autor == "Perito"
        assert m.tamanho_bytes == 50000

    def test_imutabilidade(self):
        m = MetadadosPDF(numero_paginas=5)
        with pytest.raises(AttributeError):
            m.numero_paginas = 10  # type: ignore

    def test_to_dict(self):
        m = MetadadosPDF(
            numero_paginas=3, titulo="Teste"
        )
        d = m.to_dict()
        assert d["numero_paginas"] == 3
        assert d["titulo"] == "Teste"


class TestMetricasRevisao:
    """Testes para MetricasRevisao."""

    def test_criacao_basica(self):
        m = MetricasRevisao(
            total_iteracoes=3,
            total_erros=5,
            tempo_processamento_seg=12.5,
        )
        assert m.total_erros == 5
        assert m.total_iteracoes == 3
        assert m.tempo_processamento_seg == 12.5

    def test_valores_padrao(self):
        m = MetricasRevisao(
            total_iteracoes=1,
            total_erros=0,
            tempo_processamento_seg=1.0,
        )
        assert m.convergiu is False
        assert m.custo_estimado_usd == 0.0
        assert m.tokens_consumidos == 0

    def test_erros_por_tipo(self):
        m = MetricasRevisao(
            total_iteracoes=1,
            total_erros=3,
            erros_por_tipo={"gramatical": 2, "tecnico": 1},
            tempo_processamento_seg=5.0,
        )
        assert m.erros_por_tipo["gramatical"] == 2
