"""
Controlador principal da aplicação.

Conecta a GUI à lógica de negócio, gerenciando
o ciclo de vida do processamento de textos.
"""

import asyncio
import os
from typing import Optional, Dict, Any

from PyQt6.QtCore import (
    QObject,
    QThread,
    pyqtSignal,
    pyqtSlot,
)

from ...infrastructure.ai.gemini_gateway import (
    GeminiGateway,
)
from ...infrastructure.ai.prompt_builder import (
    PromptBuilder,
)
from ...infrastructure.ai.agents import (
    AgenteRevisor,
    AgenteValidador,
    AgenteConsistencia,
)
from ...infrastructure.pdf.pdf_processor import (
    PdfProcessor,
)
from ...infrastructure.reports.markdown_generator import (
    MarkdownReportGenerator,
)
from ...infrastructure.reports.html_generator import (
    HtmlReportGenerator,
)
from ...infrastructure.repositories.json_texto_repository import (
    JsonTextoRepository,
)
from ...infrastructure.repositories.json_config_repository import (
    JsonConfigRepository,
)
from ...infrastructure.logging.app_logger import (
    AppLogger,
)
from ...application.services.orquestrador_revisao import (
    OrquestradorRevisao,
)
from ...application.use_cases.processar_texto.dto import (
    ProcessarTextoOutputDTO,
    ProgressoDTO,
)


class WorkerProcessamento(QThread):
    """
    Worker thread para processamento assíncrono.

    Executa o pipeline de revisão em thread
    separada para manter a GUI responsiva.

    Signals:
        progresso: Atualização de progresso
        concluido: Processamento finalizado
        erro: Erro durante processamento
    """

    progresso = pyqtSignal(str, float, str)
    concluido = pyqtSignal(object)
    erro = pyqtSignal(str)

    def __init__(
        self,
        orquestrador: OrquestradorRevisao,
        caminho_arquivo: str,
        formatos: list,
    ) -> None:
        super().__init__()
        self._orquestrador = orquestrador
        self._caminho_arquivo = caminho_arquivo
        self._formatos = formatos
        self._interromper = False
    
    def parar(self) -> None:
        """Sinaliza para interromper o processamento."""
        self._interromper = True

    def _check_cancel(self) -> None:
        """Verifica se o cancelamento foi solicitado."""
        if self._interromper:
            raise Exception("Processamento interrompido pelo usuário.")

    def run(self) -> None:
        """Executa processamento em thread."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            def callback_progresso(
                dto: ProgressoDTO,
            ) -> None:
                self.progresso.emit(
                    dto.etapa,
                    dto.percentual,
                    dto.mensagem,
                )

            resultado = loop.run_until_complete(
                self._orquestrador.processar_texto(
                    caminho_arquivo=self._caminho_arquivo,
                    formatos=self._formatos,
                    callback_progresso=(
                        callback_progresso
                    ),
                    check_cancel=self._check_cancel,
                )
            )

            # Limpar tarefas pendentes antes de fechar o loop
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
            loop.close()
            self.concluido.emit(resultado)

        except Exception as e:
            self.erro.emit(str(e))


class ControladorPrincipal(QObject):
    """
    Controlador principal conectando GUI e negócio.

    Gerencia a inicialização dos serviços, execução
    do processamento e comunicação de resultados.

    Signals:
        progresso_atualizado: Progresso do processamento
        processamento_concluido: Resultado final
        processamento_erro: Erro no processamento
    """

    progresso_atualizado = pyqtSignal(
        str, float, str
    )
    processamento_concluido = pyqtSignal(object)
    processamento_erro = pyqtSignal(str)
    log_recebido = pyqtSignal(str, str)  # (nivel, msg)

    def __init__(self) -> None:
        super().__init__()
        self._worker = None
        self._gateway = None
        self._config_repo = JsonConfigRepository()
        self._logger = AppLogger()
        self._orquestrador = None

        # Conectar logs detalhados à GUI
        self._logger.log_emitter.log_message.connect(
            self.log_recebido
        )

        self._inicializar_servicos()

    def _inicializar_servicos(self) -> None:
        """Inicializa todos os serviços."""
        config = self._config_repo.carregar_configuracao()

        # Consolidar API keys do ambiente
        api_keys = config.get("api_keys", {})
        if not api_keys.get("gemini") and os.environ.get("GEMINI_API_KEY"):
            api_keys["gemini"] = os.environ.get("GEMINI_API_KEY")
        if not api_keys.get("groq") and os.environ.get("GROQ_API_KEY"):
            api_keys["groq"] = os.environ.get("GROQ_API_KEY")
        if not api_keys.get("openrouter") and os.environ.get("OPENROUTER_API_KEY"):
            api_keys["openrouter"] = os.environ.get("OPENROUTER_API_KEY")
        
        config["api_keys"] = api_keys

        # Criar gateway via Factory
        from ...infrastructure.ai.ai_gateway_factory import AIGatewayFactory
        self._gateway = AIGatewayFactory.criar(config)

        prompt_builder = PromptBuilder()

        # Múltiplos agentes de revisão
        agente_gramatical = AgenteRevisor(
            self._gateway, prompt_builder,
            tipo_revisao="revisao_gramatical",
        )
        agente_tecnico = AgenteRevisor(
            self._gateway, prompt_builder,
            tipo_revisao="revisao_tecnica",
        )
        agente_validador = AgenteValidador(
            self._gateway, prompt_builder,
        )
        agente_consistencia = AgenteConsistencia(
            self._gateway, prompt_builder
        )

        # Geradores de relatório
        self._geradores = {
            "markdown": MarkdownReportGenerator(),
            "html": HtmlReportGenerator(),
        }

        # Repositório
        self._texto_repo = JsonTextoRepository(
            diretorio=config.get(
                "diretorio_dados", "./data/textos"
            )
        )

        # Orquestrador inicial (usando config padrão da inicialização)
        self._recriar_orquestrador()

    def _recriar_orquestrador(self) -> None:
        """Recria o orquestrador com base no mapeamento de fases."""
        config_base = self._config_repo.carregar_configuracao()
        perfis = config_base.get("ai_profiles", {})
        mapping = config_base.get("phase_mapping", {})
        
        # 1. Preparar configs para cada perfil
        configs = {}
        for nome_perfil in ["simples", "padrao", "complexo"]:
            cfg = dict(config_base) # Cópia base
            perfil_data = perfis.get(nome_perfil, {})
            
            if perfil_data.get("provider"):
                cfg["provider"] = perfil_data["provider"]
            if perfil_data.get("model"):
                p = cfg["provider"]
                if p == "gemini": cfg["model_gemini"] = perfil_data["model"]
                elif p == "groq": cfg["model_groq"] = perfil_data["model"]
                elif p == "openrouter": cfg["model_openrouter"] = perfil_data["model"]
            if perfil_data.get("temperatura"):
                cfg["temperatura_revisao"] = perfil_data["temperatura"]
            
            configs[nome_perfil] = cfg

        # 2. Criar Gateways
        from ...infrastructure.ai.ai_gateway_factory import AIGatewayFactory
        gateways = {
            "simples": AIGatewayFactory.criar(configs["simples"]),
            "padrao": AIGatewayFactory.criar(configs["padrao"]),
            "complexo": AIGatewayFactory.criar(configs["complexo"]),
        }
        
        # Gateway principal (usado para validações gerais)
        # Usamos o padrão como fallback
        self._gateway = gateways["padrao"]
        prompt_builder = PromptBuilder()

        # 3. Determinar fases ativas pelo mapeamento em si
        def get_gateway_for_phase(fase_key: str):
            perfil_mapeado = mapping.get(fase_key)
            if not perfil_mapeado: return None # Desativado
            return gateways.get(perfil_mapeado)

        # Construir lista de agentes revisores
        agentes_revisores = []
        
        gw_gramatical = get_gateway_for_phase("gramatical")
        if gw_gramatical:
            agentes_revisores.append(AgenteRevisor(
                gw_gramatical, prompt_builder, tipo_revisao="revisao_gramatical"
            ))
            
        gw_tecnica = get_gateway_for_phase("tecnica")
        if gw_tecnica:
             agentes_revisores.append(AgenteRevisor(
                gw_tecnica, prompt_builder, tipo_revisao="revisao_tecnica"
            ))
            
        gw_estrutural = get_gateway_for_phase("estrutural")
        if gw_estrutural:
             agentes_revisores.append(AgenteRevisor(
                gw_estrutural, prompt_builder, tipo_revisao="revisao_estrutural"
            ))
        
        # Agentes opcionais
        agente_validador = None
        gw_validacao = get_gateway_for_phase("validacao")
        if gw_validacao:
            agente_validador = AgenteValidador(gw_validacao, prompt_builder)
            
        agente_consistencia = None
        gw_consistencia = get_gateway_for_phase("consistencia")
        if gw_consistencia:
            agente_consistencia = AgenteConsistencia(gw_consistencia, prompt_builder)

        self._orquestrador = OrquestradorRevisao(
            pdf_processor=PdfProcessor(),
            agentes_revisores=agentes_revisores,
            agente_validador=agente_validador,
            agente_consistencia=agente_consistencia,
            texto_repo=self._texto_repo,
            config_repo=self._config_repo,
            geradores_relatorio=self._geradores,
            logger=self._logger,
        )

    @pyqtSlot(str, list)
    def processar_texto(
        self,
        caminho_arquivo: str,
        formatos: list = None,
    ) -> None:
        """
        Inicia processamento de texto.

        Args:
            caminho_arquivo: Caminho do arquivo
            formatos: Formatos de relatório
        """
        if formatos is None:
            formatos = ["markdown", "html"]

        if self._worker and self._worker.isRunning():
            self.processamento_erro.emit(
                "Processamento já em andamento"
            )
            return

        if not self._orquestrador:
             self.processamento_erro.emit("IA não configurada corretamente.")
             return

        self._worker = WorkerProcessamento(
            self._orquestrador,
            caminho_arquivo,
            formatos,
        )
        self._worker.progresso.connect(
            self.progresso_atualizado
        )
        self._worker.concluido.connect(
            self._on_concluido
        )
        self._worker.erro.connect(
            self._on_erro
        )
        self._worker.start()

    @pyqtSlot()
    def interromper_processamento(self) -> None:
        """Interrompe o processamento atual."""
        if self._worker and self._worker.isRunning():
            self._logger.warning("Solicitando interrupção do processamento...")
            self._worker.parar()

    @pyqtSlot(object)
    def _on_concluido(self, resultado) -> None:
        """Callback de conclusão."""
        self.processamento_concluido.emit(resultado)

    @pyqtSlot(str)
    def _on_erro(self, mensagem: str) -> None:
        """Callback de erro."""
        self.processamento_erro.emit(mensagem)

    def obter_configuracao(self) -> Dict[str, Any]:
        """Retorna configuração atual."""
        return self._config_repo.carregar_configuracao()

    def salvar_configuracao(
        self, config: Dict[str, Any]
    ) -> None:
        """Salva configuração e reinicializa."""
        self._config_repo.salvar_configuracao(config)
        self._inicializar_servicos()

    def obter_metricas_ia(self) -> Dict[str, Any]:
        """Retorna métricas de uso da IA."""
        if self._gateway:
            return self._gateway.obter_metricas()
        return {
            "total_requests": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "total_erros": 0,
            "tempo_total_seg": 0.0,
        }
