from unittest.mock import MagicMock
from src.infrastructure.reports.markdown_generator import MarkdownReportGenerator
from src.infrastructure.reports.html_generator import HtmlReportGenerator
from src.core.entities.texto_estruturado import TextoEstruturado
from src.core.entities.secao import Secao
from src.core.entities.erro import Erro
from src.core.enums.tipo_erro import TipoErro

# Setup data
import os
# Setup data
import os
from src.core.enums.status_texto import StatusTexto
with open('dummy.pdf', 'wb') as f:
    f.write(b'%PDF-1.4')
t = TextoEstruturado(
    caminho_arquivo='dummy.pdf',
    nome_arquivo='dummy.pdf',
    status=StatusTexto.PROCESSANDO,
    metadados=MagicMock(),
    tamanho_bytes=100,
    numero_paginas=1
)
s = Secao('Test Section', 'content', 1, 1, 1)
e = Erro(
    tipo=TipoErro.GRAMATICAL,
    descricao='My Justification for Error',
    trecho_original='wrong text',
    sugestao_correcao='right text',
    severidade=1,
    agente_origem='agent'
)

# Mock methods that would trigger database/logic
s.adicionar_revisao(MagicMock())
s.obter_todos_erros = MagicMock(return_value=[e])
t.adicionar_secao(s)

# Generate reports
md_content = MarkdownReportGenerator().gerar(t).conteudo
html_content = HtmlReportGenerator().gerar(t).conteudo

# Verify
print("Markdown Check:")
if "| Justificativa |" in md_content and "My Justification for Error" in md_content:
    print("PASS: Justificativa column and content found.")
else:
    print("FAIL: Justificativa missing in MD\n", md_content)

print("\nHTML Check:")
if "<th>Justificativa</th>" in html_content and "My Justification for Error" in html_content:
    print("PASS: Justificativa column and content found.")
else:
    print("FAIL: Justificativa missing in HTML\n", html_content)
