"""
Widget de resultados simplificado.

Exibe apenas os botões de ação após conclusão,
sem pré-visualização detalhada (substituída pelo log).
"""

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)
from PyQt6.QtCore import pyqtSignal, Qt


class ResultadosWidget(QWidget):
    """
    Widget para ações pós-revisão.

    Exibe botões para abrir relatórios quando
    o processamento é concluído com sucesso.
    Signals:
        relatorio_solicitado: Emitido quando o
            usuário solicita abrir o relatório.
    """

    relatorio_solicitado = pyqtSignal(str)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura interface do widget."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 24, 0, 0)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._btn_md = QPushButton("📄 Relatório Markdown")
        self._btn_md.setObjectName("btn_secondary")
        self._btn_md.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_md.clicked.connect(
            lambda: self.relatorio_solicitado.emit("markdown")
        )
        self._btn_md.hide()
        layout.addWidget(self._btn_md)

        self._btn_html = QPushButton("🌐 Relatório HTML")
        self._btn_html.setObjectName("btn_secondary")
        self._btn_html.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_html.clicked.connect(
            lambda: self.relatorio_solicitado.emit("html")
        )
        self._btn_html.hide()
        layout.addWidget(self._btn_html)

    def carregar_resultados(self, texto: object) -> None:
        """
        Ativa exibição dos botões.

        Args:
            texto: Ignorado (mantido por compatibilidade)
        """
        self._btn_md.show()
        self._btn_html.show()

    def limpar(self) -> None:
        """Reseta estado (oculta botões)."""
        self._btn_md.hide()
        self._btn_html.hide()
