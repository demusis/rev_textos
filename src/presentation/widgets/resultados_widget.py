"""
Widget de resultados de revisão.

Exibe os resultados da revisão em formato tabular
e com resumo visual por seção.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGroupBox,
    QTextEdit,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from ..tema import Tema
from ...core.entities.texto_estruturado import TextoEstruturado


class ResultadosWidget(QWidget):
    """
    Widget para exibição dos resultados da revisão.

    Organiza resultados em abas: resumo geral,
    erros por seção e texto revisado.

    Signals:
        relatorio_solicitado: Emitido quando o
            usuário solicita abrir o relatório.
    """

    relatorio_solicitado = pyqtSignal(str)

    def __init__(
        self, parent: QWidget = None
    ) -> None:
        super().__init__(parent)
        self._texto = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura interface do widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(16)

        # Tabs de resultados
        self._tabs = QTabWidget()

        # Tab 1: Resumo
        self._tab_resumo = QWidget()
        self._setup_tab_resumo()
        self._tabs.addTab(
            self._tab_resumo, "📊 Resumo"
        )

        # Tab 2: Erros
        self._tab_erros = QWidget()
        self._setup_tab_erros()
        self._tabs.addTab(
            self._tab_erros, "⚠️ Erros"
        )

        # Tab 3: Texto Revisado
        self._tab_texto = QWidget()
        self._setup_tab_texto()
        self._tabs.addTab(
            self._tab_texto, "📝 Texto"
        )

        layout.addWidget(self._tabs)

    def _setup_tab_resumo(self) -> None:
        """Configura aba de resumo."""
        layout = QVBoxLayout(self._tab_resumo)

        # Métricas cards
        metricas_layout = QHBoxLayout()

        self._card_secoes = self._criar_metrica_card(
            "Seções", "0", Tema.COR_INFO
        )
        self._card_erros = self._criar_metrica_card(
            "Erros", "0", Tema.COR_ERRO
        )
        self._card_progresso = (
            self._criar_metrica_card(
                "Progresso", "0%", Tema.COR_SUCESSO
            )
        )
        self._card_status = (
            self._criar_metrica_card(
                "Status", "—", Tema.COR_PRIMARIA
            )
        )

        metricas_layout.addWidget(self._card_secoes)
        metricas_layout.addWidget(self._card_erros)
        metricas_layout.addWidget(
            self._card_progresso
        )
        metricas_layout.addWidget(self._card_status)
        layout.addLayout(metricas_layout)

        # Tabela resumo por seção
        self._tabela_resumo = QTableWidget()
        self._tabela_resumo.setColumnCount(4)
        self._tabela_resumo.setHorizontalHeaderLabels(
            ["Seção", "Erros", "Iterações", "Status"]
        )
        header = (
            self._tabela_resumo.horizontalHeader()
        )
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for i in range(1, 4):
            header.setSectionResizeMode(
                i,
                QHeaderView.ResizeMode.ResizeToContents,
            )
        self._tabela_resumo.verticalHeader().hide()
        self._tabela_resumo.setAlternatingRowColors(
            True
        )
        layout.addWidget(self._tabela_resumo)

        # Botões de ação
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_abrir_md = QPushButton(
            "📄 Abrir Relatório Markdown"
        )
        btn_abrir_md.setObjectName("btn_secondary")
        btn_abrir_md.clicked.connect(
            lambda: self.relatorio_solicitado.emit(
                "markdown"
            )
        )
        btn_layout.addWidget(btn_abrir_md)

        btn_abrir_html = QPushButton(
            "🌐 Abrir Relatório HTML"
        )
        btn_abrir_html.setObjectName("btn_secondary")
        btn_abrir_html.clicked.connect(
            lambda: self.relatorio_solicitado.emit(
                "html"
            )
        )
        btn_layout.addWidget(btn_abrir_html)
        layout.addLayout(btn_layout)

    def _setup_tab_erros(self) -> None:
        """Configura aba de erros."""
        layout = QVBoxLayout(self._tab_erros)

        self._tabela_erros = QTableWidget()
        self._tabela_erros.setColumnCount(6)
        self._tabela_erros.setHorizontalHeaderLabels(
            [
                "Seção",
                "Tipo",
                "Sev.",
                "Original",
                "Correção",
                "Status",
            ]
        )
        header = (
            self._tabela_erros.horizontalHeader()
        )
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            5, QHeaderView.ResizeMode.ResizeToContents
        )
        self._tabela_erros.verticalHeader().hide()
        self._tabela_erros.setAlternatingRowColors(
            True
        )
        layout.addWidget(self._tabela_erros)

    def _setup_tab_texto(self) -> None:
        """Configura aba de texto revisado."""
        layout = QVBoxLayout(self._tab_texto)

        self._texto_revisado = QTextEdit()
        self._texto_revisado.setReadOnly(True)
        self._texto_revisado.setFont(
            QFont(
                Tema.FONT_MONO,
                Tema.FONT_SIZE_NORMAL,
            )
        )
        layout.addWidget(self._texto_revisado)

    def _criar_metrica_card(
        self,
        titulo: str,
        valor: str,
        cor: str,
    ) -> QGroupBox:
        """Cria card de métrica minimalista."""
        card = QGroupBox()
        card.setStyleSheet(
            f"QGroupBox {{ "
            f"background: {Tema.BG_CARD}; "
            f"border: 1px solid {Tema.BORDA}; "
            f"border-radius: 8px; "
            f"margin-top: 0; "
            f"}}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(4)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName(f"valor_{titulo}")
        lbl_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_valor.setStyleSheet(
            f"font-family: '{Tema.FONT_PRINCIPAL}'; "
            f"font-size: 24pt; "
            f"font-weight: 700; "
            f"color: {cor};"
        )
        card_layout.addWidget(lbl_valor)

        lbl_titulo = QLabel(titulo.upper())
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet(
            f"font-family: '{Tema.FONT_PRINCIPAL}'; "
            f"font-size: 8pt; "
            f"font-weight: 600; "
            f"color: {Tema.TEXTO_SECUNDARIO}; "
            f"letter-spacing: 1px;"
        )
        card_layout.addWidget(lbl_titulo)

        return card

    def carregar_resultados(
        self, texto: TextoEstruturado
    ) -> None:
        """
        Carrega resultados do texto processado.

        Args:
            texto: Texto com resultados
        """
        self._texto = texto
        self._atualizar_resumo()
        self._atualizar_erros()
        self._atualizar_texto()

    def _atualizar_resumo(self) -> None:
        """Atualiza aba de resumo."""
        if not self._texto:
            return

        texto = self._texto

        # Cards de métricas
        self._atualizar_valor_card(
            self._card_secoes, str(len(texto.secoes))
        )
        self._atualizar_valor_card(
            self._card_erros,
            str(texto.total_erros_encontrados),
        )
        self._atualizar_valor_card(
            self._card_progresso,
            f"{texto.progresso_percentual:.0f}%",
        )
        self._atualizar_valor_card(
            self._card_status, texto.status.value
        )

        # Tabela resumo
        self._tabela_resumo.setRowCount(
            len(texto.secoes)
        )
        for i, secao in enumerate(texto.secoes):
            self._tabela_resumo.setItem(
                i,
                0,
                QTableWidgetItem(secao.titulo),
            )
            self._tabela_resumo.setItem(
                i,
                1,
                QTableWidgetItem(
                    str(
                        len(
                            secao.obter_todos_erros()
                        )
                    )
                ),
            )
            self._tabela_resumo.setItem(
                i,
                2,
                QTableWidgetItem(
                    str(secao.total_iteracoes)
                ),
            )
            self._tabela_resumo.setItem(
                i,
                3,
                QTableWidgetItem(
                    secao.status.value
                ),
            )

    def _atualizar_erros(self) -> None:
        """Atualiza aba de erros."""
        if not self._texto:
            return

        todos_erros = []
        for secao in self._texto.secoes:
            for erro in secao.obter_todos_erros():
                todos_erros.append(
                    (secao.titulo, erro)
                )

        self._tabela_erros.setRowCount(
            len(todos_erros)
        )
        for i, (titulo, erro) in enumerate(
            todos_erros
        ):
            self._tabela_erros.setItem(
                i, 0, QTableWidgetItem(titulo)
            )
            self._tabela_erros.setItem(
                i,
                1,
                QTableWidgetItem(erro.tipo.value),
            )

            # Severidade com cor
            sev_item = QTableWidgetItem(
                "⚠️" * erro.severidade
            )
            self._tabela_erros.setItem(
                i, 2, sev_item
            )

            self._tabela_erros.setItem(
                i,
                3,
                QTableWidgetItem(
                    erro.trecho_original[:60]
                ),
            )
            self._tabela_erros.setItem(
                i,
                4,
                QTableWidgetItem(
                    erro.sugestao_correcao[:60]
                ),
            )

            status = (
                "✅ Aceito"
                if erro.aceito
                else "❌ Rejeitado"
                if erro.aceito is False
                else "⏳ Pendente"
            )
            self._tabela_erros.setItem(
                i,
                5,
                QTableWidgetItem(status),
            )

    def _atualizar_texto(self) -> None:
        """Atualiza aba de texto revisado."""
        if not self._texto:
            return

        partes = []
        for secao in self._texto.secoes:
            partes.append(
                f"═══ {secao.titulo} ═══\n"
            )
            if secao.revisoes:
                ultima = secao.revisoes[-1]
                texto = getattr(
                    ultima,
                    "texto_saida",
                    secao.conteudo_original,
                )
                partes.append(
                    texto or secao.conteudo_original
                )
            else:
                partes.append(
                    secao.conteudo_original
                )
            partes.append("\n")

        self._texto_revisado.setPlainText(
            "\n".join(partes)
        )

    def _atualizar_valor_card(
        self, card: QGroupBox, valor: str
    ) -> None:
        """Atualiza valor exibido no card."""
        layout = card.layout()
        if layout and layout.count() > 0:
            item = layout.itemAt(0)
            if item and item.widget():
                item.widget().setText(valor)

    def limpar(self) -> None:
        """Limpa todos os resultados."""
        self._texto = None
        self._tabela_resumo.setRowCount(0)
        self._tabela_erros.setRowCount(0)
        self._texto_revisado.clear()
        self._atualizar_valor_card(
            self._card_secoes, "0"
        )
        self._atualizar_valor_card(
            self._card_erros, "0"
        )
        self._atualizar_valor_card(
            self._card_progresso, "0%"
        )
        self._atualizar_valor_card(
            self._card_status, "—"
        )
