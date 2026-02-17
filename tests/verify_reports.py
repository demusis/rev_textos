import sys
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Add src to path - assuming run from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.entities.texto_estruturado import TextoEstruturado
from src.core.entities.secao import Secao
from src.core.entities.revisao import Revisao
from src.core.entities.erro import Erro
from src.core.enums.status_texto import StatusTexto
from src.core.enums.tipo_erro import TipoErro
from src.core.value_objects.localizacao_erro import LocalizacaoErro
from src.infrastructure.reports.markdown_generator import MarkdownReportGenerator
from src.infrastructure.reports.html_generator import HtmlReportGenerator

def test_reports():
    # Create dummy file
    dummy_path = "test_dummy.pdf"
    with open(dummy_path, "wb") as f:
        f.write(b"%PDF-1.4 dummy content")

    try:
        # Create mock data
        texto = TextoEstruturado(
            caminho_arquivo=os.path.abspath(dummy_path),
            nome_arquivo="test.pdf",
            data_carregamento=datetime.now() - timedelta(minutes=2, seconds=30)
        )
        texto.status = StatusTexto.CONCLUIDO
        
        secao = Secao(titulo="Introduction", numero_pagina_inicio=1, numero_pagina_fim=2, conteudo_original="dummy content")
        secao.status = StatusTexto.CONCLUIDO
        
        erro = Erro(
            tipo=TipoErro.GRAMATICAL,
            trecho_original="testting",
            sugestao_correcao="testing",
            descricao="Spelling error",
            severidade=2,
            localizacao=LocalizacaoErro(pagina=1)
        )
        revisao = Revisao(numero_iteracao=1, texto_entrada="dummy content")
        revisao.adicionar_erro(erro)
        secao.adicionar_revisao(revisao)
        texto.adicionar_secao(secao)
        
        # Test Markdown
        md_gen = MarkdownReportGenerator()
        relatorio_md = md_gen.gerar(texto)
        
        print("--- Markdown Check ---")
        if "Tempo Processamento" in relatorio_md.conteudo:
            print("PASS: 'Tempo Processamento' found in Markdown.")
        else:
            print("FAIL: 'Tempo Processamento' NOT found in Markdown.")
            
        if "Severidade" not in relatorio_md.conteudo and "⚠️" not in relatorio_md.conteudo:
            print("PASS: 'Severidade' column removed from Markdown.")
        else:
            print("FAIL: 'Severidade' or emoji found in Markdown.")
    
        # Test HTML
        html_gen = HtmlReportGenerator()
        relatorio_html = html_gen.gerar(texto)
        
        print("\n--- HTML Check ---")
        if "Tempo Processamento" in relatorio_html.conteudo:
            print("PASS: 'Tempo Processamento' found in HTML.")
        else:
            print("FAIL: 'Tempo Processamento' NOT found in HTML.")
            
        if "Sev." not in relatorio_html.conteudo and "class=\"severidade\"" not in relatorio_html.conteudo:
            print("PASS: 'Sev.' column removed from HTML.")
        else:
            print("FAIL: 'Sev.' or class='severidade' found in HTML.")

    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)

if __name__ == "__main__":
    test_reports()
