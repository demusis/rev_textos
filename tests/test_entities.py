"""Testes das entidades do domínio."""

import os
import pytest

from src.core.entities.erro import Erro
from src.core.entities.correcao import Correcao
from src.core.entities.revisao import Revisao
from src.core.entities.secao import Secao
from src.core.entities.texto_estruturado import TextoEstruturado
from src.core.entities.relatorio import Relatorio
from src.core.enums.status_texto import StatusTexto
from src.core.enums.tipo_erro import TipoErro
from src.core.enums.formato_relatorio import (
    FormatoRelatorio,
)
from src.core.value_objects.metadados_pdf import (
    MetadadosPDF,
)


class TestErro:
    """Testes para entidade Erro."""

    def test_criacao(self):
        e = Erro(
            tipo=TipoErro.GRAMATICAL,
            descricao="Erro de concordância",
            trecho_original="foi encontrado",
            sugestao_correcao="foram encontrados",
            severidade=3,
        )
        assert e.tipo == TipoErro.GRAMATICAL
        assert e.severidade == 3
        assert e.aceito is None

    def test_aceitar_erro(self):
        e = Erro(
            tipo=TipoErro.GRAMATICAL,
            descricao="Typo",
            trecho_original="exmplo",
            sugestao_correcao="exemplo",
            severidade=2,
        )
        e.aceitar()
        assert e.aceito is True

    def test_rejeitar_erro(self):
        e = Erro(
            tipo=TipoErro.TECNICO,
            descricao="Erro técnico",
            trecho_original="a",
            sugestao_correcao="b",
            severidade=1,
        )
        e.rejeitar()
        assert e.aceito is False

    def test_to_dict_from_dict(self):
        e = Erro(
            tipo=TipoErro.GRAMATICAL,
            descricao="Desc",
            trecho_original="abc",
            sugestao_correcao="def",
            severidade=2,
        )
        d = e.to_dict()
        e2 = Erro.from_dict(d)
        assert e2.tipo == e.tipo
        assert e2.descricao == e.descricao
        assert e2.trecho_original == e.trecho_original

    def test_severidade_valida(self):
        with pytest.raises(Exception):
            Erro(
                tipo=TipoErro.GRAMATICAL,
                descricao="X",
                trecho_original="a",
                sugestao_correcao="b",
                severidade=0,
            )

    def test_severidade_max(self):
        with pytest.raises(Exception):
            Erro(
                tipo=TipoErro.GRAMATICAL,
                descricao="X",
                trecho_original="a",
                sugestao_correcao="b",
                severidade=11,
            )


class TestRevisao:
    """Testes para entidade Revisao."""

    def test_criacao(self):
        r = Revisao(
            numero_iteracao=1,
            texto_entrada="Texto original",
        )
        assert r.numero_iteracao == 1
        assert r.texto_entrada == "Texto original"
        assert r.erros == []

    def test_adicionar_erro(self):
        r = Revisao(
            numero_iteracao=1,
            texto_entrada="Texto",
        )
        e = Erro(
            tipo=TipoErro.GRAMATICAL,
            descricao="D",
            trecho_original="a",
            sugestao_correcao="b",
            severidade=1,
        )
        r.adicionar_erro(e)
        assert len(r.erros) == 1

    def test_finalizar(self):
        r = Revisao(
            numero_iteracao=1,
            texto_entrada="T",
        )
        r.finalizar()
        assert r.esta_finalizada is True

    def test_to_dict_from_dict(self):
        r = Revisao(
            numero_iteracao=2,
            texto_entrada="Texto",
        )
        d = r.to_dict()
        r2 = Revisao.from_dict(d)
        assert r2.numero_iteracao == 2
        assert r2.texto_entrada == "Texto"


class TestSecao:
    """Testes para entidade Secao."""

    def test_criacao(self):
        s = Secao(
            titulo="INTRODUÇÃO",
            conteudo_original="Texto intro.",
            numero_pagina_inicio=1,
            numero_pagina_fim=3,
        )
        assert s.titulo == "INTRODUÇÃO"
        assert s.numero_pagina_inicio == 1

    def test_adicionar_revisao(self):
        s = Secao(
            titulo="INTRO",
            conteudo_original="T",
            numero_pagina_inicio=1,
            numero_pagina_fim=1,
        )
        r = Revisao(
            numero_iteracao=1, texto_entrada="T"
        )
        s.adicionar_revisao(r)
        assert s.total_iteracoes == 1

    def test_obter_todos_erros(self):
        s = Secao(
            titulo="S",
            conteudo_original="T",
            numero_pagina_inicio=1,
            numero_pagina_fim=1,
        )
        r = Revisao(
            numero_iteracao=1, texto_entrada="T"
        )
        e = Erro(
            tipo=TipoErro.GRAMATICAL,
            descricao="D",
            trecho_original="a",
            sugestao_correcao="b",
            severidade=1,
        )
        r.adicionar_erro(e)
        s.adicionar_revisao(r)
        erros = s.obter_todos_erros()
        assert len(erros) == 1

    def test_to_dict_from_dict(self):
        s = Secao(
            titulo="TITULO",
            conteudo_original="Conteúdo",
            numero_pagina_inicio=2,
            numero_pagina_fim=5,
        )
        d = s.to_dict()
        s2 = Secao.from_dict(d)
        assert s2.titulo == "TITULO"
        assert s2.numero_pagina_inicio == 2


class TestTextoEstruturado:
    """Testes para entidade TextoEstruturado (aggregate root)."""

    @pytest.fixture
    def pdf_fake(self, tmp_path):
        pdf = tmp_path / "teste.pdf"
        pdf.write_bytes(b"%PDF fake content")
        return str(pdf)

    def test_criacao(self, pdf_fake):
        texto = TextoEstruturado(
            caminho_arquivo=pdf_fake,
            nome_arquivo="teste.pdf",
            metadados=MetadadosPDF(numero_paginas=5),
            tamanho_bytes=os.path.getsize(pdf_fake),
            numero_paginas=5,
        )
        assert texto.nome_arquivo == "teste.pdf"
        assert texto.status == StatusTexto.PENDENTE

    def test_adicionar_secao(self, pdf_fake):
        texto = TextoEstruturado(
            caminho_arquivo=pdf_fake,
            nome_arquivo="teste.pdf",
            metadados=MetadadosPDF(numero_paginas=5),
            tamanho_bytes=os.path.getsize(pdf_fake),
            numero_paginas=5,
        )
        s = Secao(
            titulo="S1",
            conteudo_original="T",
            numero_pagina_inicio=1,
            numero_pagina_fim=2,
        )
        texto.adicionar_secao(s)
        assert len(texto.secoes) == 1

    def test_atualizar_status(self, pdf_fake):
        texto = TextoEstruturado(
            caminho_arquivo=pdf_fake,
            nome_arquivo="teste.pdf",
            metadados=MetadadosPDF(numero_paginas=5),
            tamanho_bytes=os.path.getsize(pdf_fake),
            numero_paginas=5,
        )
        texto.atualizar_status(
            StatusTexto.PROCESSANDO
        )
        assert (
            texto.status
            == StatusTexto.PROCESSANDO
        )

    def test_calcular_hash(self, pdf_fake):
        texto = TextoEstruturado(
            caminho_arquivo=pdf_fake,
            nome_arquivo="teste.pdf",
            metadados=MetadadosPDF(numero_paginas=5),
            tamanho_bytes=os.path.getsize(pdf_fake),
            numero_paginas=5,
        )
        texto.calcular_hash()
        assert texto.hash_arquivo
        assert len(texto.hash_arquivo) > 10

    def test_total_erros(self, pdf_fake):
        texto = TextoEstruturado(
            caminho_arquivo=pdf_fake,
            nome_arquivo="teste.pdf",
            metadados=MetadadosPDF(numero_paginas=5),
            tamanho_bytes=os.path.getsize(pdf_fake),
            numero_paginas=5,
        )
        s = Secao(
            titulo="S",
            conteudo_original="T",
            numero_pagina_inicio=1,
            numero_pagina_fim=1,
        )
        r = Revisao(
            numero_iteracao=1, texto_entrada="T"
        )
        r.adicionar_erro(
            Erro(
                tipo=TipoErro.GRAMATICAL,
                descricao="D",
                trecho_original="a",
                sugestao_correcao="b",
                severidade=1,
            )
        )
        r.adicionar_erro(
            Erro(
                tipo=TipoErro.TECNICO,
                descricao="D2",
                trecho_original="c",
                sugestao_correcao="d",
                severidade=2,
            )
        )
        r.finalizar()
        s.adicionar_revisao(r)
        texto.adicionar_secao(s)
        assert texto.total_erros_encontrados == 2

    def test_to_dict_from_dict(self, pdf_fake):
        texto = TextoEstruturado(
            caminho_arquivo=pdf_fake,
            nome_arquivo="teste.pdf",
            metadados=MetadadosPDF(numero_paginas=3),
            tamanho_bytes=os.path.getsize(pdf_fake),
            numero_paginas=3,
        )
        texto.calcular_hash()
        d = texto.to_dict()
        texto2 = TextoEstruturado.from_dict(d)
        assert texto2.nome_arquivo == "teste.pdf"
        assert texto2.numero_paginas == 3


class TestRelatorio:
    """Testes para entidade Relatorio."""

    def test_criacao(self):
        r = Relatorio(
            titulo="Revisão",
            formato=FormatoRelatorio.MARKDOWN,
            conteudo="# Relatório",
            texto_nome="documento.pdf",
            total_secoes=5,
            total_erros=10,
        )
        assert r.titulo == "Revisão"
        assert r.formato == FormatoRelatorio.MARKDOWN
        assert r.total_erros == 10
