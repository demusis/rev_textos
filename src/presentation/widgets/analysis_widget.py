"""
Widget de análise (Progresso + Resultados).

Container que gerencia a exibição do progresso
e dos resultados da revisão.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal

from .progresso_widget import ProgressoWidget
from .resultados_widget import ResultadosWidget
from ..tema import Tema


class AnalysisWidget(QWidget):
    """
    Tela de análise ativa.

    Contém:
    - Widget de progresso (topo)
    - Widget de resultados (centro)
    - Botões de ação (fundo)
    """

    voltar_clicked = pyqtSignal()
    relatorio_solicitado = pyqtSignal(str)
    cancelar_processamento = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura interface de análise."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Cabeçalho com botão voltar (opcional se sidebar existir)
        # Manteremos simples por enquanto

        # Progresso
        # Progresso (expande para ocupar espaço)
        self.progresso = ProgressoWidget()
        self.progresso.cancelar_clicked.connect(self._on_cancelar)
        layout.addWidget(self.progresso, stretch=1)

        # Resultados (inicialmente oculto ou vazio)
        self.resultados = ResultadosWidget()
        self.resultados.relatorio_solicitado.connect(
            self.relatorio_solicitado
        )
        # O resultado (botões) fica no fundo com tamanho fixo
        layout.addWidget(self.resultados)

    def resetar(self) -> None:
        """Reseta widgets internos."""
        self.progresso.resetar()
        self.resultados.limpar()

    def carregar_resultados(self, texto) -> None:
        """Carrega resultados no widget."""
        self.resultados.carregar_resultados(texto)

    def atualizar_progresso(
        self,
        etapa: str,
        percentual: float,
        mensagem: str,
    ) -> None:
        """Atualiza progresso."""
        self.progresso.atualizar_progresso(
            etapa, percentual, mensagem
        )

    def _on_cancelar(self) -> None:
        """Handler para botão interromper."""
        self.cancelar_processamento.emit()
