"""Configuração de testes pytest."""

import sys
from pathlib import Path
import pytest
from PyQt6.QtWidgets import QApplication

# Adicionar src ao path
sys.path.insert(
    0, str(Path(__file__).parent.parent)
)

@pytest.fixture(scope="session")
def qapp():
    """Fixture para QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
