
import asyncio
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    filename="reproduce_debug.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.infrastructure.repositories.json_config_repository import JsonConfigRepository
from src.infrastructure.repositories.json_texto_repository import JsonTextoRepository
from src.infrastructure.ai.prompt_builder import PromptBuilder
from src.infrastructure.ai.ai_gateway_factory import AIGatewayFactory
from src.infrastructure.ai.agents import AgenteRevisor, AgenteValidador, AgenteConsistencia
from src.infrastructure.pdf.pdf_processor import PdfProcessor
from src.infrastructure.reports.markdown_generator import MarkdownReportGenerator
from src.infrastructure.reports.html_generator import HtmlReportGenerator
from src.infrastructure.logging.app_logger import AppLogger
from src.application.services.orquestrador_revisao import OrquestradorRevisao
from src.application.use_cases.processar_texto.dto import ProgressoDTO

async def main():
    print("Iniciando reprodução do erro...")
    
    # Setup dependencies manually to avoid PyQt
    config_repo = JsonConfigRepository()
    config = config_repo.carregar_configuracao()
    
    # Mock API keys if needed (or rely on existing config)
    # config["api_keys"] = {"groq": "mock_key"}
    
    gateway = AIGatewayFactory.criar(config)
    prompt_builder = PromptBuilder()
    
    agente_gramatical = AgenteRevisor(gateway, prompt_builder, "revisao_gramatical")
    agente_tecnico = AgenteRevisor(gateway, prompt_builder, "revisao_tecnica")
    agente_validador = AgenteValidador(gateway, prompt_builder)
    agente_consistencia = AgenteConsistencia(gateway, prompt_builder)
    
    geradores = {
        "markdown": MarkdownReportGenerator(),
        "html": HtmlReportGenerator(),
    }
    
    texto_repo = JsonTextoRepository(config.get("diretorio_dados", "./data/textos"))
    logger = AppLogger()
    
    orquestrador = OrquestradorRevisao(
        pdf_processor=PdfProcessor(),
        agentes_revisores=[agente_gramatical, agente_tecnico],
        agente_validador=agente_validador,
        agente_consistencia=agente_consistencia,
        texto_repo=texto_repo,
        config_repo=config_repo,
        geradores_relatorio=geradores,
        logger=logger,
    )
    
    def callback(dto: ProgressoDTO):
        print(f"Progresso: {dto.percentual}% - {dto.mensagem}")
    
    try:
        # Full path to dummy.tex
        caminho = os.path.abspath("dummy.tex")
        print(f"Processando arquivo: {caminho}")
        
        resultado = await orquestrador.processar_texto(
            caminho_arquivo=caminho,
            formatos=["markdown", "html"],
            callback_progresso=callback
        )
        print("Resultado:", resultado)
        
    except Exception as e:
        with open("reproduce_log_utf8.txt", "w", encoding="utf-8") as f:
            f.write("\n!!! ERRO CAPTURADO !!!\n")
            f.write(str(e) + "\n")
            import traceback
            traceback.print_exc(file=f)
        print("\n!!! ERRO CAPTURADO !!! Check reproduce_log_utf8.txt")

if __name__ == "__main__":
    asyncio.run(main())
