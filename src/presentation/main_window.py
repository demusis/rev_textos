"""
Janela principal da aplicação.

Interface central que integra a barra lateral,
área de conteúdo (Home/Análise) e controlador.
"""

import os
import webbrowser

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox,
    QStatusBar,
)
from PyQt6.QtCore import QSize, QTimer
from PyQt6.QtGui import QIcon

from .tema import Tema
from .widgets.sidebar_widget import SidebarWidget
from .widgets.home_widget import HomeWidget
from .widgets.analysis_widget import AnalysisWidget
from .controllers.controlador_principal import (
    ControladorPrincipal,
)
from .dialogs.config_dialog import ConfigDialog


class MainWindow(QMainWindow):
    """
    Janela principal com navegação lateral e conteúdo em pilha.
    """

    def __init__(self) -> None:
        super().__init__()
        self._controlador = ControladorPrincipal()
        self._ultimo_resultado = None
        self._setup_ui()
        self._conectar_sinais()

        # Timer para atualizar métricas da IA
        self._timer_metricas = QTimer(self)
        self._timer_metricas.timeout.connect(
            self._atualizar_metricas_ia
        )
        self._timer_metricas.start(2000)

    def _setup_ui(self) -> None:
        """Configura interface principal."""
        self.setWindowTitle("Revisor de Textos Estruturados")
        self.resize(1200, 800)
        self.setMinimumSize(QSize(900, 600))

        # Widget central (Container horizontal)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra Lateral
        self._sidebar = SidebarWidget()
        self._sidebar.pagina_alterada.connect(self._mudar_pagina)
        self._sidebar.btn_config.clicked.connect(self._abrir_config)
        self._sidebar.btn_ajuda.clicked.connect(self._mostrar_sobre)
        layout.addWidget(self._sidebar)

        # Área de Conteúdo (Pilha de Widgets)
        self._stack = QStackedWidget()
        
        # Página 0: Home
        self._home = HomeWidget()
        self._home.processar_clicked.connect(
            self._iniciar_processamento
        )
        self._stack.addWidget(self._home)

        # Página 1: Análise (Progresso + Resultados)
        self._analysis = AnalysisWidget()
        self._analysis.relatorio_solicitado.connect(
            self._abrir_relatorio
        )
        self._stack.addWidget(self._analysis)

        layout.addWidget(self._stack)

        # Status Bar (Minimalista)
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Pronto")
        
        self._atualizar_info_provedor()

    def _conectar_sinais(self) -> None:
        """Conecta sinais globalmente."""
        self._controlador.progresso_atualizado.connect(
            self._analysis.atualizar_progresso
        )
        self._controlador.processamento_concluido.connect(
            self._on_processamento_concluido
        )
        self._controlador.processamento_erro.connect(
            self._on_processamento_erro
        )

    def _mudar_pagina(self, index: int) -> None:
        """Alterna página exibida na pilha."""
        self._stack.setCurrentIndex(index)

    def _iniciar_processamento(
        self, caminho: str, formatos: list
    ) -> None:
        """Inicia processamento e muda para análise."""
        self._analysis.resetar()
        
        # Muda para tela de análise e habilita botão na sidebar
        self._sidebar.habilitar_resultados()
        
        self._status_bar.showMessage("Processando...")
        self._controlador.processar_texto(caminho, formatos)

    def _on_processamento_concluido(
        self, resultado
    ) -> None:
        """Callback de sucesso."""
        self._ultimo_resultado = resultado
        
        if resultado.sucesso and resultado.texto:
            self._analysis.carregar_resultados(
                resultado.texto
            )
            self._status_bar.showMessage(
                f"Concluído — {resultado.texto.total_erros_encontrados} "
                f"erros encontrados"
            )
        else:
            self._status_bar.showMessage("Erro no processamento")
            self._stack.setCurrentIndex(0)  # Volta à Home
            self._home.habilitar_processar(True)
            QMessageBox.warning(
                self, "Atenção", resultado.mensagem
            )

    def _on_processamento_erro(self, mensagem: str) -> None:
        """Callback de erro."""
        self._status_bar.showMessage("Erro no processamento")
        self._stack.setCurrentIndex(0)  # Volta à Home
        self._home.habilitar_processar(True)
        QMessageBox.critical(
            self, "Erro no Processamento", mensagem
        )

    def _abrir_config(self) -> None:
        """Abre configurações."""
        config = self._controlador.obter_configuracao()
        dialog = ConfigDialog(config, self)
        if dialog.exec():
            nova_config = dialog.obter_config()
            self._controlador.salvar_configuracao(nova_config)
            self._atualizar_info_provedor()
            self._status_bar.showMessage("Configurações salvas")
        
        # Remove seleção do botão
        self._sidebar.btn_config.setChecked(False)

    def _atualizar_info_provedor(self) -> None:
        """Atualiza info do provedor na Home."""
        config = self._controlador.obter_configuracao()
        provider = config.get("provider", "gemini").capitalize()
        model_key = f"model_{provider.lower()}"
        model = config.get(model_key, config.get("gemini_model", "?"))
        self._home.definir_info_provedor(provider, model)

    def _abrir_relatorio(self, formato: str) -> None:
        """Abre relatório no app padrão."""
        if (
            self._ultimo_resultado
            and self._ultimo_resultado.relatorios
        ):
            caminho = self._ultimo_resultado.relatorios.get(
                formato
            )
            if caminho and os.path.exists(caminho):
                webbrowser.open(caminho)
            else:
                QMessageBox.information(
                    self,
                    "Relatório",
                    f"Relatório {formato} não encontrado.",
                )

    def _mostrar_sobre(self) -> None:
        """Exibe sobre."""
        QMessageBox.about(
            self,
            "Sobre",
            "<h2>Revisor de Textos Estruturados</h2>"
            "<p>v1.1.0 (Clean UI)</p>"
            "<p>Interface moderna e sóbria para revisão "
            "automática de textos estruturados com IA.</p>"
        )
        self._sidebar.btn_ajuda.setChecked(False)

    def _atualizar_metricas_ia(self) -> None:
        """Atualiza métricas de IA na sidebar."""
        metricas = (
            self._controlador.obter_metricas_ia()
        )
        self._sidebar.atualizar_metricas(metricas)
