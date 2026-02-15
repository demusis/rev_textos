"""
Widget da tela inicial (Home).

Contém a seleção de arquivos e botão de processamento
em um layout limpo e centralizado.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QFileDialog,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..tema import Tema


class HomeWidget(QWidget):
    """
    Tela inicial para iniciar nova revisão.

    Signals:
        arquivo_selecionado(str): Caminho do arquivo
        processar_clicked(str, list): Caminho, formatos
    """

    processar_clicked = pyqtSignal(str, list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._caminho_arquivo = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura interface da home."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(32)

        # Container centralizado
        container = QWidget()
        container.setStyleSheet(
            f"background-color: {Tema.BG_CARD}; "
            f"border-radius: 12px; "
            f"border: 1px solid {Tema.BORDA};"
        )
        # Sombra sutil simulada via borda dupla ou gradiente (opcional)
        # Simplificado para Clean Design

        cont_layout = QVBoxLayout(container)
        cont_layout.setContentsMargins(40, 40, 40, 40)
        cont_layout.setSpacing(24)

        # Área de seleção (Input grande)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)

        self._txt_arquivo = QLineEdit()
        self._txt_arquivo.setPlaceholderText(
            "Selecione o arquivo (PDF, DOCX, ODT, TEX, MD)..."
        )
        self._txt_arquivo.setReadOnly(True)
        self._txt_arquivo.setMinimumHeight(48)
        self._txt_arquivo.setStyleSheet(
            f"font-size: 11pt; padding-left: 16px;"
        )
        input_layout.addWidget(self._txt_arquivo)

        self._btn_selecionar = QPushButton("📂 Procurar")
        self._btn_selecionar.setMinimumHeight(48)
        self._btn_selecionar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self._btn_selecionar.setStyleSheet(
            f"font-size: 11pt; padding: 0 24px;"
        )
        self._btn_selecionar.clicked.connect(
            self._selecionar_arquivo
        )
        input_layout.addWidget(self._btn_selecionar)

        cont_layout.addLayout(input_layout)

        # Checkboxes
        opts_layout = QHBoxLayout()
        opts_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        opts_layout.setSpacing(32)

        self._chk_md = QCheckBox("Relatório Markdown")
        self._chk_md.setChecked(True)
        self._chk_md.setStyleSheet(
            f"font-size: 11pt; color: {Tema.TEXTO_PRIMARIO};"
        )
        
        self._chk_html = QCheckBox("Relatório HTML")
        self._chk_html.setChecked(True)
        self._chk_html.setStyleSheet(
            f"font-size: 11pt; color: {Tema.TEXTO_PRIMARIO};"
        )

        opts_layout.addWidget(self._chk_md)
        opts_layout.addWidget(self._chk_html)
        cont_layout.addLayout(opts_layout)

        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {Tema.BORDA};")
        cont_layout.addWidget(line)

        # Botão Iniciar
        self._btn_iniciar = QPushButton("Iniciar revisão")
        self._btn_iniciar.setObjectName("btn_processar")
        self._btn_iniciar.setMinimumHeight(56)
        self._btn_iniciar.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self._btn_iniciar.setEnabled(False)
        self._btn_iniciar.setStyleSheet(
            f"""
            QPushButton#btn_processar {{
                font-size: 12pt;
                font-weight: 700;
                padding: 12px 32px;
                color: #ffffff;
                background-color: {Tema.COR_PRIMARIA};
                border-radius: 8px;
            }}
            QPushButton#btn_processar:disabled {{
                background-color: {Tema.BORDA};
                color: {Tema.TEXTO_MUTED};
            }}
            """
        )
        self._btn_iniciar.clicked.connect(self._iniciar)
        cont_layout.addWidget(self._btn_iniciar)

        cont_layout.addWidget(self._btn_iniciar)

        # Info do Provedor (Rodapé do Card)
        self._lbl_provider = QLabel("")
        self._lbl_provider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_provider.setStyleSheet(
            f"color: {Tema.TEXTO_SECUNDARIO}; font-size: 10pt; margin-top: 8px;"
        )
        cont_layout.addWidget(self._lbl_provider)

        # Adiciona ao layout principal (centralizado verticalmente)
        layout.addStretch()
        layout.addWidget(container)
        layout.addStretch()

    def definir_info_provedor(self, provider: str, model: str) -> None:
        """Atualiza label com info do provedor."""
        self._lbl_provider.setText(f"🤖 IA: {provider} | Modelo: {model}")

    def habilitar_processar(self, habilitado: bool = True) -> None:
        """Habilita/desabilita o botão de iniciar processamento."""
        self._btn_iniciar.setEnabled(habilitado)

    def _selecionar_arquivo(self) -> None:
        """Abre diálogo de arquivo."""
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Texto Estruturado",
            "",
            "Documentos suportados (*.pdf *.docx *.odt *.tex *.md);;"
            "PDF (*.pdf);;"
            "Word (*.docx);;"
            "OpenOffice (*.odt);;"
            "LaTeX (*.tex);;"
            "Markdown (*.md);;"
            "Todos os arquivos (*.*)",
        )
        if caminho:
            self._caminho_arquivo = caminho
            self._txt_arquivo.setText(caminho)
            self._btn_iniciar.setEnabled(True)

    def _iniciar(self) -> None:
        """Emite sinal para iniciar processamento."""
        if not self._caminho_arquivo:
            return

        formatos = []
        if self._chk_md.isChecked():
            formatos.append("markdown")
        if self._chk_html.isChecked():
            formatos.append("html")
        
        if not formatos:
            formatos = ["markdown"]

        self.processar_clicked.emit(
            self._caminho_arquivo, formatos
        )
