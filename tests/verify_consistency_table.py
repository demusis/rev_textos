
import json
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(str(Path(__file__).parent))

from src.core.entities.texto_estruturado import TextoEstruturado
from src.infrastructure.reports.markdown_generator import MarkdownReportGenerator
from src.infrastructure.reports.html_generator import HtmlReportGenerator

def test_consistency_rendering():
    # 1. Criar dado Mock de inconsistência (JSON)
    consistencia_json = {
        "inconsistencias": [
            {
                "secao_1": "1. Identificação do atendimento pericial",
                "secao_2": "4.1 Itens recebidos (formais)",
                "descricao": "A data da vistoria pericial é informada como 19/01/2026, porém um dos documentos formais recebidos é um 'Relatório fotográfico' intitulado 'vistoria 18-01-2026'.",
                "severidade": 4,
                "sugestao": "Confirmar a data correta da vistoria."
            },
            {
                "secao_1": "1. Identificação",
                "secao_2": "3. Quesitos",
                "descricao": "Divergência de datas entre recebimento de quesitos e vistoria.",
                "severidade": 3,
                "sugestao": "Explicitar base legal."
            }
        ],
        "consistente": False,
        "resumo": "Foram encontradas inconsistências críticas relacionadas a datas."
    }

    # 2. Criar entidade de texto
    texto = TextoEstruturado(
        caminho_arquivo="laudo_teste.docx",
        nome_arquivo="laudo_teste.docx"
    )
    texto.analise_consistencia = json.dumps(consistencia_json, ensure_ascii=False)
    texto.info_ia = {"provedor": "Gemini", "modelo": "2.0-flash"}

    # 3. Gerar relatórios
    output_dir = "temp_verification"
    
    # Markdown
    md_gen = MarkdownReportGenerator()
    rel_md = md_gen.gerar(texto)
    md_path = md_gen.salvar(rel_md, output_dir)
    print(f"Relatório MD gerado em: {md_path}")
    
    # HTML
    html_gen = HtmlReportGenerator()
    rel_html = html_gen.gerar(texto)
    html_path = html_gen.salvar(rel_html, output_dir)
    print(f"Relatório HTML gerado em: {html_path}")

    # Verificar se a tabela está presente (verificação simples de string)
    with open(md_path, "r", encoding="utf-8") as f:
        content_md = f.read()
        if "| Seção 1 | Seção 2 |" in content_md:
            print("✅ Tabela encontrada no Markdown")
        else:
            print("❌ Tabela NÃO encontrada no Markdown")

    with open(html_path, "r", encoding="utf-8") as f:
        content_html = f.read()
        if "<table>" in content_html and "Seção 1</th>" in content_html:
            print("✅ Tabela encontrada no HTML")
        else:
            print("❌ Tabela NÃO encontrada no HTML")
            print(content_html)

if __name__ == "__main__":
    test_consistency_rendering()
