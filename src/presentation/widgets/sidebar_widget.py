"""
Widget de barra lateral para navegação.

Menu vertical com ícones e botões para
alternar entre as visões da aplicação.
Inclui painel de métricas de uso da IA.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont

from ..tema import Tema


class SidebarWidget(QWidget):
    """
    Barra lateral de navegação.

    Signals:
        pagina_alterada(int): Índice da página selecionada
    """

    pagina_alterada = pyqtSignal(int)

    # Índices das páginas
    PAGINA_HOME = 0
    PAGINA_RESULTADOS = 1
    PAGINA_HISTORICO = 2

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura interface da sidebar."""
        self.setFixedWidth(240)
        self.setStyleSheet(
            f"background-color: {Tema.BG_CARD}; "
            f"border-right: 1px solid {Tema.BORDA};"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(8)

        # Título / Logo
        lbl_titulo = QLabel("REVISOR\nTEXTOS")
        lbl_titulo.setAlignment(
            Qt.AlignmentFlag.AlignLeft
        )
        lbl_titulo.setStyleSheet(
            f"font-family: '{Tema.FONT_PRINCIPAL}'; "
            f"font-size: 16pt; "
            f"font-weight: 800; "
            f"color: {Tema.COR_PRIMARIA}; "
            f"margin-bottom: 24px;"
        )
        layout.addWidget(lbl_titulo)

        # Botões de navegação
        self._btn_home = self._criar_botao(
            "📝 Nova Revisão", True
        )
        self._btn_home.clicked.connect(
            lambda: self._navegar(self.PAGINA_HOME)
        )
        layout.addWidget(self._btn_home)

        self._btn_resultados = self._criar_botao(
            "📊 Resultados", False
        )
        self._btn_resultados.setVisible(False)
        self._btn_resultados.clicked.connect(
            lambda: self._navegar(
                self.PAGINA_RESULTADOS
            )
        )
        layout.addWidget(self._btn_resultados)

        layout.addStretch()

        # ━━━ Painel de métricas de IA ━━━
        self._metricas_frame = QFrame()
        self._metricas_frame.setStyleSheet(
            f"QFrame {{"
            f"  background-color: {Tema.BG_PRINCIPAL};"
            f"  border: 1px solid {Tema.BORDA};"
            f"  border-radius: 8px;"
            f"  padding: 8px;"
            f"}}"
        )
        metricas_layout = QVBoxLayout(
            self._metricas_frame
        )
        metricas_layout.setContentsMargins(
            10, 8, 10, 8
        )
        metricas_layout.setSpacing(4)

        lbl_titulo_m = QLabel("📊 Uso da IA (sessão)")
        lbl_titulo_m.setStyleSheet(
            f"font-size: 9pt; "
            f"font-weight: 700; "
            f"color: {Tema.TEXTO_PRIMARIO}; "
            f"border: none; "
            f"margin-bottom: 4px;"
        )
        metricas_layout.addWidget(lbl_titulo_m)

        estilo_metrica = (
            f"font-family: '{Tema.FONT_MONO}'; "
            f"font-size: 8pt; "
            f"color: {Tema.TEXTO_SECUNDARIO}; "
            f"border: none;"
        )

        self._lbl_requests = QLabel(
            "Requisições: 0"
        )
        self._lbl_requests.setStyleSheet(
            estilo_metrica
        )
        metricas_layout.addWidget(self._lbl_requests)

        self._lbl_tokens_in = QLabel("Tokens ↑: 0")
        self._lbl_tokens_in.setStyleSheet(
            estilo_metrica
        )
        metricas_layout.addWidget(
            self._lbl_tokens_in
        )

        self._lbl_tokens_out = QLabel("Tokens ↓: 0")
        self._lbl_tokens_out.setStyleSheet(
            estilo_metrica
        )
        metricas_layout.addWidget(
            self._lbl_tokens_out
        )

        self._lbl_erros = QLabel("Erros: 0")
        self._lbl_erros.setStyleSheet(estilo_metrica)
        metricas_layout.addWidget(self._lbl_erros)

        self._lbl_tempo = QLabel("Tempo: 0.0s")
        self._lbl_tempo.setStyleSheet(estilo_metrica)
        metricas_layout.addWidget(self._lbl_tempo)

        layout.addWidget(self._metricas_frame)

        # Botões inferiores (Config e Sobre)
        divisor = QFrame()
        divisor.setFrameShape(QFrame.Shape.HLine)
        divisor.setStyleSheet(
            f"color: {Tema.BORDA};"
        )
        layout.addWidget(divisor)

        self.btn_config = self._criar_botao(
            "⚙️ Configurações", False
        )
        layout.addWidget(self.btn_config)

        self.btn_ajuda = self._criar_botao(
            "❓ Ajuda", False
        )
        layout.addWidget(self.btn_ajuda)

    def _criar_botao(
        self, texto: str, checked: bool
    ) -> QPushButton:
        """Cria botão de menu estilizado."""
        btn = QPushButton(texto)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        btn.setFixedHeight(48)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                text-align: left;
                padding-left: 16px;
                border: none;
                border-radius: 8px;
                background-color: transparent;
                color: {Tema.TEXTO_SECUNDARIO};
                font-weight: 600;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {Tema.BG_HOVER};
                color: {Tema.COR_PRIMARIA};
            }}
            QPushButton:checked {{
                background-color: {Tema.BG_HOVER};
                color: {Tema.COR_PRIMARIA};
                border-left: 4px solid \
{Tema.COR_PRIMARIA};
                font-weight: 700;
            }}
            """
        )
        return btn

    def _navegar(self, index: int) -> None:
        """Navega para página e atualiza botões."""
        self._btn_home.setChecked(
            index == self.PAGINA_HOME
        )
        self._btn_resultados.setChecked(
            index == self.PAGINA_RESULTADOS
        )

        self.pagina_alterada.emit(index)

    def habilitar_resultados(self) -> None:
        """Habilita botão de resultados."""
        self._btn_resultados.setVisible(True)
        self._navegar(self.PAGINA_RESULTADOS)

    def atualizar_metricas(
        self, metricas: dict
    ) -> None:
        """Atualiza painel de métricas da IA."""
        req = metricas.get("total_requests", 0)
        t_in = metricas.get(
            "total_tokens_input", 0
        )
        t_out = metricas.get(
            "total_tokens_output", 0
        )
        erros = metricas.get("total_erros", 0)
        tempo = metricas.get(
            "tempo_total_seg", 0.0
        )

        self._lbl_requests.setText(
            f"Requisições: {req}"
        )

        # Formatar tokens de forma legível
        def _fmt(n):
            if n >= 1_000_000:
                return f"{n / 1_000_000:.1f}M"
            elif n >= 1_000:
                return f"{n / 1_000:.1f}k"
            return str(n)

        self._lbl_tokens_in.setText(
            f"Tokens ↑: {_fmt(t_in)}"
        )
        self._lbl_tokens_out.setText(
            f"Tokens ↓: {_fmt(t_out)}"
        )
        self._lbl_erros.setText(f"Erros: {erros}")

        # Formatar tempo
        if tempo >= 60:
            mins = int(tempo // 60)
            secs = tempo % 60
            self._lbl_tempo.setText(
                f"Tempo: {mins}m {secs:.0f}s"
            )
        else:
            self._lbl_tempo.setText(
                f"Tempo: {tempo:.1f}s"
            )
