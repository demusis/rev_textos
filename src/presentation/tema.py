"""
Sistema de tema e estilos da GUI.

Define paleta de cores sóbria, fontes e StyleSheet
global para a aplicação PyQt6.
"""


class Tema:
    """
    Tema visual da aplicação (Sóbrio/Profissional).
    """

    # Paleta de Cores (Slate/Gray Neutral)
    COR_PRIMARIA = "#334155"        # Slate 700
    COR_PRIMARIA_CLARO = "#475569"  # Slate 600
    COR_PRIMARIA_HOVER = "#1e293b"  # Slate 800
    
    COR_ACCENT = "#0ea5e9"          # Sky 500 (Destaques sutis)
    
    COR_SUCESSO = "#059669"         # Emerald 600
    COR_ERRO = "#dc2626"            # Red 600
    COR_AVISO = "#d97706"           # Amber 600
    COR_INFO = "#0284c7"            # Sky 600

    # Backgrounds
    BG_PRINCIPAL = "#f8fafc"        # Slate 50
    BG_CARD = "#ffffff"             # White
    BG_HEADER = "#ffffff"           # White (Clean)
    BG_INPUT = "#ffffff"            # White
    BG_HOVER = "#f1f5f9"            # Slate 100

    # Texto
    TEXTO_PRIMARIO = "#0f172a"      # Slate 900
    TEXTO_SECUNDARIO = "#64748b"    # Slate 500
    TEXTO_CLARO = "#ffffff"         # White
    TEXTO_MUTED = "#94a3b8"         # Slate 400

    # Bordas
    BORDA = "#e2e8f0"               # Slate 200
    BORDA_CLARA = "#f1f5f9"         # Slate 100
    BORDA_FOCUS = "#0ea5e9"         # Sky 500

    # Fontes
    FONT_PRINCIPAL = "Segoe UI"
    FONT_MONO = "Consolas"
    FONT_SIZE_TITULO = 16
    FONT_SIZE_SUBTITULO = 13
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_SMALL = 9

    # Dimensões
    BORDER_RADIUS = 6
    PADDING = 16
    SPACING = 12

    @classmethod
    def stylesheet(cls) -> str:
        """Retorna StyleSheet global da aplicação."""
        return f"""
        /* === GLOBAL === */
        QMainWindow, QDialog, QMessageBox {{
            background-color: {cls.BG_PRINCIPAL};
        }}

        QWidget {{
            font-family: '{cls.FONT_PRINCIPAL}';
            font-size: {cls.FONT_SIZE_NORMAL}pt;
            color: {cls.TEXTO_PRIMARIO};
        }}

        /* === DIALOGS === */
        QMessageBox QLabel {{
            color: {cls.TEXTO_PRIMARIO};
            font-size: {cls.FONT_SIZE_NORMAL}pt;
        }}
        
        QDialog QLabel {{
            color: {cls.TEXTO_PRIMARIO};
        }}

        /* === BOTÕES === */
        QPushButton {{
            background-color: {cls.BG_CARD};
            color: {cls.TEXTO_PRIMARIO};
            border: 1px solid {cls.BORDA};
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: {cls.FONT_SIZE_NORMAL}pt;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: {cls.BG_HOVER};
            border-color: {cls.TEXTO_MUTED};
        }}
        QPushButton:pressed {{
            background-color: {cls.BORDA};
        }}
        QPushButton:disabled {{
            background-color: {cls.BG_PRINCIPAL};
            color: {cls.TEXTO_MUTED};
            border-color: {cls.BORDA};
        }}
        
        QPushButton#btn_processar {{
            background-color: {cls.COR_PRIMARIA};
            color: {cls.TEXTO_CLARO};
            border: none;
            padding: 10px 24px;
        }}
        QPushButton#btn_processar:hover {{
            background-color: {cls.COR_PRIMARIA_HOVER};
        }}
        
        QPushButton#btn_secondary {{
            background-color: transparent;
            color: {cls.COR_PRIMARIA};
            border: 1px solid {cls.BORDA};
        }}
        QPushButton#btn_secondary:hover {{
            background-color: {cls.BG_HOVER};
            border-color: {cls.COR_PRIMARIA};
        }}
        
        QPushButton#btn_action {{
            background-color: {cls.COR_INFO};
            color: {cls.TEXTO_CLARO};
            border: none;
        }}
        QPushButton#btn_action:hover {{
            background-color: #0369a1;
        }}

        /* === INPUTS === */
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
            background-color: {cls.BG_INPUT};
            border: 1px solid {cls.BORDA};
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 8px 12px;
            selection-background-color: {cls.COR_ACCENT};
            selection-color: {cls.TEXTO_CLARO};
            color: {cls.TEXTO_PRIMARIO};
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 1px solid {cls.BORDA_FOCUS};
            background-color: {cls.BG_CARD};
        }}
        
        QLineEdit:read-only {{
            background-color: {cls.BG_PRINCIPAL};
            color: {cls.TEXTO_SECUNDARIO};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 2px solid {cls.BORDA};
            width: 0;
            height: 0;
            border-top: 5px solid {cls.TEXTO_SECUNDARIO};
            border-right: 5px solid transparent;
            border-bottom: 0;
            border-left: 5px solid transparent;
            margin-top: 2px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {cls.BG_CARD};
            color: {cls.TEXTO_PRIMARIO};
            selection-background-color: {cls.BG_HOVER};
            selection-color: {cls.TEXTO_PRIMARIO};
            border: 1px solid {cls.BORDA};
            outline: none;
        }}

        /* === LABELS === */
        QLabel#titulo {{
            font-size: {cls.FONT_SIZE_TITULO}pt;
            font-weight: 700;
            color: {cls.TEXTO_PRIMARIO};
        }}
        QLabel#subtitulo {{
            font-size: {cls.FONT_SIZE_SUBTITULO}pt;
            font-weight: 500;
            color: {cls.TEXTO_SECUNDARIO};
        }}
        QLabel#label_info {{
            color: {cls.TEXTO_SECUNDARIO};
        }}

        /* === PROGRESS BAR === */
        QProgressBar {{
            border: none;
            border-radius: 4px;
            background-color: {cls.BORDA};
            text-align: center;
            font-size: 9pt;
            font-weight: 600;
            color: {cls.TEXTO_PRIMARIO};
            min-height: 18px;
            max-height: 18px;
        }}
        QProgressBar::chunk {{
            background-color: {cls.COR_ACCENT};
            border-radius: 4px;
        }}

        /* === GROUP BOX (Clean) === */
        QGroupBox {{
            background-color: {cls.BG_CARD};
            border: 1px solid {cls.BORDA};
            border-radius: {cls.BORDER_RADIUS}px;
            margin-top: 12px;
            padding: 24px 16px 16px 16px;
            font-weight: 600;
            color: {cls.TEXTO_PRIMARIO};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            left: 8px;
            color: {cls.TEXTO_SECUNDARIO};
            background-color: {cls.BG_CARD};
        }}

        /* === TABLES === */
        QTableWidget {{
            background-color: {cls.BG_CARD};
            border: 1px solid {cls.BORDA};
            border-radius: {cls.BORDER_RADIUS}px;
            gridline-color: {cls.BORDA_CLARA};
            selection-background-color: {cls.BG_HOVER};
            selection-color: {cls.TEXTO_PRIMARIO};
        }}
        QHeaderView::section {{
            background-color: {cls.BG_PRINCIPAL};
            color: {cls.TEXTO_PRIMARIO};
            padding: 8px;
            border: none;
            border-bottom: 2px solid {cls.BORDA};
            font-weight: 600;
            text-transform: uppercase;
            font-size: 8pt;
        }}
        QTableCornerButton::section {{
            background-color: {cls.BG_PRINCIPAL};
            border: none;
            border-bottom: 1px solid {cls.BORDA};
            border-right: 1px solid {cls.BORDA};
        }}

        /* === TABS === */
        QTabWidget::pane {{
            border: 1px solid {cls.BORDA};
            border-radius: {cls.BORDER_RADIUS}px;
            background: {cls.BG_CARD};
            top: -1px;
        }}
        QTabBar::tab {{
            background: transparent;
            color: {cls.TEXTO_SECUNDARIO};
            padding: 10px 20px;
            margin-right: 4px;
            border-bottom: 2px solid transparent;
            font-weight: 600;
        }}
        QTabBar::tab:selected {{
            color: {cls.COR_PRIMARIA};
            border-bottom: 2px solid {cls.COR_PRIMARIA};
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {cls.BG_HOVER};
            border-radius: 4px;
        }}

        /* === SCROLLBAR (Modern Slim) === */
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 8px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {cls.BORDA};
            border-radius: 4px;
            min-height: 40px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {cls.TEXTO_MUTED};
        }}
        QScrollBar:add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 8px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background: {cls.BORDA};
            border-radius: 4px;
            min-width: 40px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {cls.TEXTO_MUTED};
        }}
        QScrollBar:add-line:horizontal, 
        QScrollBar::sub-line:horizontal {{
            width: 0;
        }}

        /* === STATUS BAR === */
        QStatusBar {{
            background-color: {cls.BG_CARD};
            color: {cls.TEXTO_SECUNDARIO};
            border-top: 1px solid {cls.BORDA};
        }}
        
        /* === MENUBAR === */
        QMenuBar {{
            background-color: {cls.BG_CARD};
            color: {cls.TEXTO_PRIMARIO};
            border-bottom: 1px solid {cls.BORDA};
        }}
        QMenuBar::item:selected {{
            background-color: {cls.BG_HOVER};
        }}
        QMenu {{
            background-color: {cls.BG_CARD};
            border: 1px solid {cls.BORDA};
            padding: 4px;
        }}
        QMenu::item {{
            padding: 6px 24px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: {cls.BG_HOVER};
        }}
        
        /* === SPLITTER === */
        QSplitter::handle {{
            background-color: {cls.BORDA};
            height: 1px;
            margin: 0 20px;
        }}
        """
