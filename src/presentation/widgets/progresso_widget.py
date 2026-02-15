"""
Widget de progresso de processamento.

Exibe barra de progresso animada, status atual
e log de atividades em tempo real.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QLabel,
    QTextEdit,
    QGroupBox,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont

from ..tema import Tema


class ProgressoWidget(QWidget):
    """
    Widget de progresso com barra, status e log.

    Exibe o andamento do processamento com:
    - Barra de progresso com percentual
    - Label de etapa atual
    - Área de log com histórico de atividades
    """

    def __init__(
        self, parent: QWidget = None
    ) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura interface do widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Card de progresso
        card = QGroupBox("Progresso")
        card_layout = QVBoxLayout(card)

        # Etapa atual
        self._lbl_etapa = QLabel("Aguardando...")
        self._lbl_etapa.setObjectName("subtitulo")
        card_layout.addWidget(self._lbl_etapa)

        # Barra de progresso
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFormat("%p% concluído")
        card_layout.addWidget(self._progress)

        # Detalhes (percentual e tempo)
        info_layout = QHBoxLayout()
        self._lbl_detalhe = QLabel("")
        self._lbl_detalhe.setStyleSheet(
            f"color: {Tema.TEXTO_SECUNDARIO}; "
            f"font-size: {Tema.FONT_SIZE_SMALL}px;"
        )
        info_layout.addWidget(self._lbl_detalhe)
        info_layout.addStretch()
        card_layout.addLayout(info_layout)

        layout.addWidget(card)

        # Log de atividades
        log_card = QGroupBox("Log de Atividades")
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(12, 24, 12, 12)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        # self._log.setMaximumHeight(300)  <-- Removido para expansão dinâmica
        self._log.setFont(
            QFont(Tema.FONT_MONO, Tema.FONT_SIZE_SMALL)
        )
        self._log.setStyleSheet(
            f"background-color: {Tema.BG_HOVER}; "
            f"color: {Tema.TEXTO_PRIMARIO}; "
            f"border: 1px solid {Tema.BORDA}; "
            f"border-radius: 4px; "
            f"padding: 8px;"
        )
        log_layout.addWidget(self._log)

        layout.addWidget(log_card, stretch=1)

    @pyqtSlot(str, float, str)
    def atualizar_progresso(
        self,
        etapa: str,
        percentual: float,
        mensagem: str,
    ) -> None:
        """
        Atualiza o progresso exibido.

        Args:
            etapa: Nome da etapa atual
            percentual: Percentual (0-100)
            mensagem: Mensagem descritiva
        """
        self._progress.setValue(int(percentual))
        self._lbl_etapa.setText(mensagem)
        self._lbl_detalhe.setText(
            f"Etapa: {etapa} — "
            f"{percentual:.0f}%"
        )
        self._adicionar_log(
            f"[{etapa.upper()}] {mensagem}"
        )

    def _adicionar_log(self, texto: str) -> None:
        """Adiciona entrada ao log, padronizando formato."""
        from datetime import datetime

        # Formato manual para alinhar com o logger do AppLogger
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg_formatada = f"{ts} | INFO     | GUI      | {texto}"
        
        # Reutiliza lógica de exibição
        self.adicionar_log_detalhado("INFO", msg_formatada)

    @pyqtSlot(str, str)
    def adicionar_log_detalhado(
        self, nivel: str, mensagem: str
    ) -> None:
        """Adiciona log detalhado vindo do sistema de logging.

        Args:
            nivel: Nível do log (INFO, WARNING, ERROR)
            mensagem: Mensagem formatada
        """
        cores = {
            "DEBUG": "#888888",
            "INFO": Tema.TEXTO_PRIMARIO,  # Padronizado para cor de texto normal
            "WARNING": "#FFA500",
            "ERROR": "#FF4444",
            "CRITICAL": "#FF0000",
        }
        cor = cores.get(nivel, Tema.TEXTO_PRIMARIO)
        self._log.append(
            f'<span style="color:{cor}">'
            f"{mensagem}</span>"
        )
        # Auto-scroll
        sb = self._log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def resetar(self) -> None:
        """Reseta widget para estado inicial."""
        self._progress.setValue(0)
        self._lbl_etapa.setText("Aguardando...")
        self._lbl_detalhe.setText("")
        self._log.clear()
