"""Testes da camada de infraestrutura."""

import asyncio
import json
import os
import tempfile
import shutil
import pytest

from src.infrastructure.ai.gemini_gateway import (
    GeminiGateway,
)
from src.infrastructure.ai.prompt_builder import (
    PromptBuilder,
)
from src.infrastructure.ai.agents import (
    AgenteRevisor,
    AgenteValidador,
    AgenteConsistencia,
)
from src.infrastructure.pdf.pdf_processor import (
    PdfProcessor,
)
from src.infrastructure.reports.markdown_generator import (
    MarkdownReportGenerator,
)
from src.infrastructure.reports.html_generator import (
    HtmlReportGenerator,
)
from src.infrastructure.repositories.json_texto_repository import (
    JsonTextoRepository,
)
from src.infrastructure.repositories.json_config_repository import (
    JsonConfigRepository,
)
from src.infrastructure.logging.app_logger import (
    AppLogger,
)
from src.core.entities.texto_estruturado import TextoEstruturado
from src.core.entities.secao import Secao
from src.core.entities.revisao import Revisao
from src.core.entities.erro import Erro
from src.core.enums.status_texto import StatusTexto
from src.core.enums.tipo_erro import TipoErro
from src.core.enums.formato_relatorio import (
    FormatoRelatorio,
)
from src.core.value_objects.metadados_pdf import (
    MetadadosPDF,
)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def pdf_fake(tmp_dir):
    path = os.path.join(tmp_dir, "teste.pdf")
    with open(path, "wb") as f:
        f.write(b"%PDF-1.4 fake content")
    return path


@pytest.fixture
def texto_sample(pdf_fake):
    texto = TextoEstruturado(
        caminho_arquivo=pdf_fake,
        nome_arquivo="teste.pdf",
        metadados=MetadadosPDF(numero_paginas=3),
        tamanho_bytes=os.path.getsize(pdf_fake),
        numero_paginas=3,
    )
    s = Secao(
        titulo="INTRO",
        conteudo_original="Texto de teste.",
        numero_pagina_inicio=1,
        numero_pagina_fim=2,
    )
    r = Revisao(
        numero_iteracao=1,
        texto_entrada="Texto de teste.",
    )
    r.adicionar_erro(
        Erro(
            tipo=TipoErro.GRAMATICAL,
            descricao="Concordância",
            trecho_original="foi",
            sugestao_correcao="foram",
            severidade=2,
        )
    )
    r.finalizar()
    s.adicionar_revisao(r)
    texto.adicionar_secao(s)
    texto.atualizar_status(StatusTexto.CONCLUIDO)
    return texto


class TestGeminiGateway:
    """Testes para GeminiGateway."""

    def test_modo_mock(self):
        gw = GeminiGateway(
            api_key="test", modo_mock=True
        )
        assert gw._model is None

    def test_mock_gerar_conteudo(self):
        gw = GeminiGateway(
            api_key="test", modo_mock=True
        )
        resultado = asyncio.run(
            gw.gerar_conteudo("prompt teste")
        )
        assert "[MOCK]" in resultado

    def test_metricas_iniciais(self):
        gw = GeminiGateway(
            api_key="test", modo_mock=True
        )
        m = gw.obter_metricas()
        assert m["total_requests"] == 0
        assert m["total_erros"] == 0

    def test_metricas_apos_request(self):
        gw = GeminiGateway(
            api_key="test", modo_mock=True
        )
        asyncio.run(gw.gerar_conteudo("teste"))
        m = gw.obter_metricas()
        assert m["total_requests"] == 1

    def test_cache(self):
        gw = GeminiGateway(
            api_key="test", modo_mock=True
        )
        r1 = asyncio.run(
            gw.gerar_conteudo("mesmo prompt")
        )
        r2 = asyncio.run(
            gw.gerar_conteudo("mesmo prompt")
        )
        assert r1 == r2

    def test_limpar_cache(self):
        gw = GeminiGateway(
            api_key="test", modo_mock=True
        )
        asyncio.run(gw.gerar_conteudo("x"))
        assert len(gw._cache) > 0
        gw.limpar_cache()
        assert len(gw._cache) == 0

    def test_resetar_metricas(self):
        gw = GeminiGateway(
            api_key="test", modo_mock=True
        )
        asyncio.run(gw.gerar_conteudo("x"))
        gw.resetar_metricas()
        m = gw.obter_metricas()
        assert m["total_requests"] == 0


class TestPromptBuilder:
    """Testes para PromptBuilder."""

    def test_listar_tipos(self):
        pb = PromptBuilder()
        tipos = pb.listar_tipos()
        assert len(tipos) == 6
        assert "revisao_gramatical" in tipos
        assert "revisao_tecnica" in tipos
        assert "revisao_estrutural" in tipos
        assert "validacao" in tipos
        assert "consistencia" in tipos
        assert "sintese" in tipos

    def test_construir_prompt(self):
        pb = PromptBuilder()
        p = pb.construir(
            "revisao_gramatical",
            texto="Texto de teste.",
        )
        assert "Texto de teste" in p
        assert len(p) > 50

    def test_tipo_invalido(self):
        pb = PromptBuilder()
        with pytest.raises(ValueError):
            pb.construir("tipo_inexistente")


class TestAgents:
    """Testes para agentes de IA."""

    @pytest.fixture
    def gateway_mock(self):
        return GeminiGateway(
            api_key="test", modo_mock=True
        )

    @pytest.fixture
    def prompt_builder(self):
        return PromptBuilder()

    def test_agente_revisor_nome(
        self, gateway_mock, prompt_builder
    ):
        ar = AgenteRevisor(
            gateway_mock, prompt_builder
        )
        assert "revisor" in ar.obter_nome()

    def test_agente_validador_nome(
        self, gateway_mock, prompt_builder
    ):
        av = AgenteValidador(
            gateway_mock, prompt_builder
        )
        assert av.obter_nome() == "validador"

    def test_agente_consistencia_nome(
        self, gateway_mock, prompt_builder
    ):
        ac = AgenteConsistencia(
            gateway_mock, prompt_builder
        )
        assert ac.obter_nome() == "consistencia"


class TestPdfProcessor:
    """Testes para PdfProcessor."""

    def test_validar_inexistente(self):
        pp = PdfProcessor()
        result = asyncio.run(
            pp.validar_pdf("inexistente.pdf")
        )
        assert result is False

    def test_validar_nao_pdf(self, tmp_dir):
        txt = os.path.join(tmp_dir, "arquivo.txt")
        with open(txt, "w") as f:
            f.write("texto")
        pp = PdfProcessor()
        result = asyncio.run(pp.validar_pdf(txt))
        assert result is False

    def test_detectar_secoes_sem_secoes(self):
        pp = PdfProcessor()
        secoes = asyncio.run(
            pp.detectar_secoes("Texto simples.", 1)
        )
        assert len(secoes) == 1
        assert secoes[0].titulo == "DOCUMENTO COMPLETO"

    def test_detectar_secoes_numeradas(self):
        pp = PdfProcessor()
        texto = (
            "1. INTRODUÇÃO\n"
            "Texto da introdução.\n\n"
            "2. METODOLOGIA\n"
            "Texto da metodologia.\n\n"
            "3. RESULTADOS\n"
            "Texto dos resultados."
        )
        secoes = asyncio.run(
            pp.detectar_secoes(texto, 5)
        )
        assert len(secoes) == 3
        assert "INTRODUÇÃO" in secoes[0].titulo
        assert "METODOLOGIA" in secoes[1].titulo

    def test_validar_markdown(self, tmp_dir):
        md_path = os.path.join(tmp_dir, "teste.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Título\n\nConteúdo do documento.")
        pp = PdfProcessor()
        result = asyncio.run(pp.validar_pdf(md_path))
        assert result is True

    def test_extrair_texto_markdown(self, tmp_dir):
        md_path = os.path.join(tmp_dir, "teste.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(
                "# Introdução\n\n"
                "Texto com **negrito** e [link](http://x.com).\n\n"
                "![img](foto.png)\n"
            )
        pp = PdfProcessor()
        texto = asyncio.run(pp.extrair_texto(md_path))
        assert "Introdução" in texto
        assert "negrito" in texto
        assert "**" not in texto
        assert "![" not in texto
        assert "link" in texto
        assert "http://x.com" not in texto

    def test_detectar_secoes_markdown(self):
        pp = PdfProcessor()
        texto = (
            "# Introdução\n"
            "Texto da introdução.\n\n"
            "## Metodologia\n"
            "Descrição da metodologia.\n\n"
            "## Resultados\n"
            "Descrição dos resultados."
        )
        secoes = asyncio.run(
            pp.detectar_secoes(texto, 1)
        )
        assert len(secoes) == 3
        assert secoes[0].titulo == "Introdução"
        assert secoes[0].nivel == 1
        assert secoes[1].titulo == "Metodologia"
        assert secoes[1].nivel == 2


class TestMarkdownGenerator:
    """Testes para gerador Markdown."""

    def test_formato(self):
        gen = MarkdownReportGenerator()
        assert (
            gen.obter_formato()
            == FormatoRelatorio.MARKDOWN
        )

    def test_gerar_relatorio(self, texto_sample):
        gen = MarkdownReportGenerator()
        rel = gen.gerar(texto_sample)
        assert "INTRO" in rel.conteudo
        assert "Resumo" in rel.conteudo
        assert rel.total_erros == 1

    def test_salvar_relatorio(
        self, texto_sample, tmp_dir
    ):
        gen = MarkdownReportGenerator()
        rel = gen.gerar(texto_sample)
        caminho = gen.salvar(rel, tmp_dir)
        assert os.path.exists(caminho)
        assert caminho.endswith(".md")
        conteudo = open(
            caminho, encoding="utf-8"
        ).read()
        assert "INTRO" in conteudo


class TestHtmlGenerator:
    """Testes para gerador HTML."""

    def test_formato(self):
        gen = HtmlReportGenerator()
        assert (
            gen.obter_formato()
            == FormatoRelatorio.HTML
        )

    def test_gerar_relatorio(self, texto_sample):
        gen = HtmlReportGenerator()
        rel = gen.gerar(texto_sample)
        assert "<html" in rel.conteudo
        assert "INTRO" in rel.conteudo
        assert "<style>" in rel.conteudo

    def test_salvar_relatorio(
        self, texto_sample, tmp_dir
    ):
        gen = HtmlReportGenerator()
        rel = gen.gerar(texto_sample)
        caminho = gen.salvar(rel, tmp_dir)
        assert os.path.exists(caminho)
        assert caminho.endswith(".html")


class TestJsonTextoRepository:
    """Testes para repositório JSON de textos."""

    def test_salvar_e_buscar(
        self, texto_sample, tmp_dir
    ):
        repo = JsonTextoRepository(
            diretorio_dados=os.path.join(
                tmp_dir, "textos"
            )
        )
        texto_sample.calcular_hash()
        repo.salvar(texto_sample)

        encontrado = repo.buscar_por_hash(
            texto_sample.hash_arquivo
        )
        assert encontrado is not None
        assert (
            encontrado.nome_arquivo
            == "teste.pdf"
        )

    def test_listar_todos(
        self, texto_sample, tmp_dir
    ):
        repo = JsonTextoRepository(
            diretorio_dados=os.path.join(
                tmp_dir, "textos"
            )
        )
        texto_sample.calcular_hash()
        repo.salvar(texto_sample)
        todos = repo.listar_todos()
        assert len(todos) == 1

    def test_buscar_inexistente(self, tmp_dir):
        repo = JsonTextoRepository(
            diretorio_dados=os.path.join(
                tmp_dir, "textos"
            )
        )
        r = repo.buscar_por_hash("nao_existe")
        assert r is None

    def test_remover(
        self, texto_sample, tmp_dir
    ):
        repo = JsonTextoRepository(
            diretorio_dados=os.path.join(
                tmp_dir, "textos"
            )
        )
        texto_sample.calcular_hash()
        repo.salvar(texto_sample)
        repo.remover(texto_sample.hash_arquivo)
        assert (
            repo.buscar_por_hash(
                texto_sample.hash_arquivo
            )
            is None
        )


class TestJsonConfigRepository:
    """Testes para repositório JSON de config."""

    def test_config_padrao(self, tmp_dir):
        repo = JsonConfigRepository(
            caminho_config=os.path.join(
                tmp_dir, "config.json"
            )
        )
        config = repo.carregar_configuracao()
        assert "gemini_model" in config
        assert (
            config["gemini_model"]
            == "gemini-2.0-flash"
        )

    def test_obter_valor(self, tmp_dir):
        repo = JsonConfigRepository(
            caminho_config=os.path.join(
                tmp_dir, "config.json"
            )
        )
        v = repo.obter_valor("max_retries")
        assert v == 3

    def test_definir_valor(self, tmp_dir):
        repo = JsonConfigRepository(
            caminho_config=os.path.join(
                tmp_dir, "config.json"
            )
        )
        repo.definir_valor("novo_campo", 42)
        assert repo.obter_valor("novo_campo") == 42

    def test_persistencia(self, tmp_dir):
        caminho = os.path.join(
            tmp_dir, "config.json"
        )
        repo = JsonConfigRepository(
            caminho_config=caminho
        )
        repo.definir_valor("teste", "abc")

        # Recarregar
        repo2 = JsonConfigRepository(
            caminho_config=caminho
        )
        assert repo2.obter_valor("teste") == "abc"


class TestAppLogger:
    """Testes para logger da aplicação."""

    def test_criar_logger(self, tmp_dir):
        log = AppLogger(
            nome="teste_log",
            diretorio_log=os.path.join(
                tmp_dir, "logs"
            ),
        )
        assert log is not None

    def test_log_info(self, tmp_dir):
        log = AppLogger(
            nome="teste_info",
            diretorio_log=os.path.join(
                tmp_dir, "logs"
            ),
        )
        # Não deve lançar exceção
        log.info("Mensagem de teste")
        log.debug("Debug")
        log.warning("Warning")
        log.error("Error")
        log.critical("Critical")

    def test_arquivo_log_criado(self, tmp_dir):
        log_dir = os.path.join(tmp_dir, "logs")
        log = AppLogger(
            nome="teste_arquivo",
            diretorio_log=log_dir,
        )
        log.info("teste")
        assert os.path.exists(
            os.path.join(
                log_dir, "revisor_textos.log"
            )
        )
