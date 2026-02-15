"""
Ponto de entrada da aplicação.

Inicializa o loop PyQt6, aplica tema e
exibe a janela principal.
"""

import sys
import os

from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.presentation.main_window import MainWindow
from src.presentation.tema import Tema

def main() -> None:
    """Ponto de entrada principal da aplicação."""
    # Habilitar High DPI
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName(
        "Revisor de Textos Estruturados"
    )
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("RevisorTextos")

    # Aplicar tema global
    app.setStyleSheet(Tema.stylesheet())

    # Criar e exibir janela principal
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
