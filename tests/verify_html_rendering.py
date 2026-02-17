
from src.infrastructure.reports.html_generator import HtmlReportGenerator
from src.core.entities.texto_estruturado import TextoEstruturado
from src.core.enums.status_texto import StatusTexto
from datetime import datetime

class MockTexto:
    def __init__(self):
        self.nome_arquivo = "teste.pdf"
        self.analise_consistencia = "**Resumo**\n- Item 1\n- Item 2\n* Italic *"
        self.sintese_geral = "Texto com **bold**."
        self.secoes = []
        self.total_erros_encontrados = 0
        self.status = StatusTexto.CONCLUIDO
        self.data_carregamento = datetime.now()
        self.progresso_percentual = 100
        self.info_ia = None

def test_rendering():
    import sys
    gen = HtmlReportGenerator()
    texto = MockTexto()
    relatorio = gen.gerar(texto)
    
    html = relatorio.conteudo
    
    # Helper para print seguro no Windows
    def safe_print(msg):
        try:
            print(msg.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
        except:
            print(msg.encode('ascii', errors='replace').decode('ascii'))

    safe_print("--- HTML Gerado (Testes) ---")
    
    if "<strong>Resumo</strong>" in html:
        safe_print("OK: Bold renderizado.")
    else:
        safe_print("ERRO: Bold não renderizado.")
        
    if "<ul><li>Item 1</li><li>Item 2</li></ul>" in html.replace("<br>", "").replace("\n", ""):
        safe_print("OK: Lista renderizada.")
    else:
        safe_print("ERRO: Lista não renderizada.")

    if "<em> Italic </em>" in html or "<em>Italic</em>" in html:
        safe_print("OK: Italic renderizado.")
    else:
        safe_print("ERRO: Italic não renderizado.")
        # Verificando o que o regex gerou para * Italic *
        import re
        res = re.sub(r'\*(.*?)\*', r'<em>\1</em>', "* Italic *")
        safe_print(f"Debug Regex Italic: '{res}'")

if __name__ == "__main__":
    test_rendering()
