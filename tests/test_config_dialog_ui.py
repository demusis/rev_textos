"""
Testes unitários para o ConfigDialog.
"""

import json
import os
from unittest.mock import patch, MagicMock
import pytest
from PyQt6.QtWidgets import QDialog

from src.presentation.dialogs.config_dialog import ConfigDialog


def test_init_config_dialog(qapp):
    """Testa inicialização do diálogo com valores."""
    config = {
        "gemini_api_key": "test_key",
        "gemini_model": "gemini-2.0-flash",
        "max_retries": 5
    }
    dialog = ConfigDialog(config)
    
    assert dialog._txt_api_key.text() == "test_key"
    assert dialog._combo_modelo.currentText() == "gemini-2.0-flash"
    assert dialog._spin_retries.value() == 5


def test_atualizar_config_from_ui(qapp):
    """Testa atualização do dicionário interno a partir da UI."""
    config = {}
    dialog = ConfigDialog(config)
    
    # Simula edição na UI
    dialog._txt_api_key.setText("new_key_123")
    dialog._spin_timeout.setValue(500)
    
    dialog._atualizar_config_from_ui()
    
    assert dialog._config["gemini_api_key"] == "new_key_123"
    assert dialog._config["timeout"] == 500


def test_exportar_config(qapp, tmp_path):
    """Testa exportação da configuração para JSON."""
    config = {"gemini_api_key": "key_export"}
    dialog = ConfigDialog(config)
    
    export_path = tmp_path / "config_export.json"
    
    # Mock QFileDialog e QMessageBox
    with patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=(str(export_path), "")):
        with patch("PyQt6.QtWidgets.QMessageBox.information") as mock_info:
            dialog._exportar_config()
            
            # Verifica se mensagem foi exibida
            mock_info.assert_called()
            
    # Verifica se arquivo foi criado
    assert export_path.exists()
    
    # Verifica conteúdo
    with open(export_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
        assert saved_data["gemini_api_key"] == "key_export"


def test_importar_config(qapp, tmp_path):
    """Testa importação da configuração via JSON."""
    config = {"gemini_api_key": "old_key"}
    dialog = ConfigDialog(config)
    
    # Cria arquivo para importar
    import_path = tmp_path / "config_import.json"
    new_data = {"gemini_api_key": "imported_key", "timeout": 500}
    with open(import_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f)
        
    # Mock QFileDialog e QMessageBox
    with patch("PyQt6.QtWidgets.QFileDialog.getOpenFileName", return_value=(str(import_path), "")):
        with patch("PyQt6.QtWidgets.QMessageBox.information") as mock_info:
            dialog._importar_config()
            
            mock_info.assert_called()
            
    # Verifica se config interna atualizou
    assert dialog._config["gemini_api_key"] == "imported_key"
    assert dialog._config["timeout"] == 500
    
    # Verifica se UI atualizou
    assert dialog._txt_api_key.text() == "imported_key"
    assert dialog._spin_timeout.value() == 500
