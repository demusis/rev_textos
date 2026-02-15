"""
Diálogo de configurações da aplicação.

Permite ao usuário configurar provedores de IA (Gemini, Groq),
parâmetros de processamento, diretórios e editar prompts.
"""

import os
import json
import logging
from typing import Dict, Any, List

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QGroupBox,
    QFileDialog,
    QCheckBox,
    QTabWidget,
    QWidget,
    QTextEdit,
    QMessageBox,
    QStackedWidget,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ..tema import Tema
from ...infrastructure.ai.ai_gateway_factory import (
    AIGatewayFactory,
)

logger = logging.getLogger(__name__)

# Labels amigáveis para os tipos de prompt
PROMPT_LABELS = {
    "revisao_gramatical": "Revisão Gramatical",
    "revisao_tecnica": "Revisão Técnica",
    "revisao_estrutural": "Revisão Estrutural",
    "validacao": "Validação",
    "consistencia": "Consistência",
    "sintese": "Síntese",
}


class _ModelFetchWorker(QThread):
    """Worker thread para buscar modelos sem bloquear a UI."""
    finished = pyqtSignal(str, list)  # (provider, modelos)

    def __init__(self, provider: str, api_key: str, parent=None) -> None:
        super().__init__(parent)
        self._provider = provider
        self._api_key = api_key

    def run(self) -> None:
        modelos = AIGatewayFactory.listar_modelos(
            self._provider, self._api_key
        )
        self.finished.emit(self._provider, modelos)


class ConfigDialog(QDialog):
    """
    Diálogo de configurações do sistema.

    Tabs:
    1. IA / Provedores: Configuração de Gemini, Groq, etc.
    2. Processamento: Parâmetros de revisão.
    3. Diretórios: Caminhos de saída e dados.
    4. Prompts: Editor de prompts.
    """

    def __init__(self, config: dict, parent=None) -> None:
        super().__init__(parent)
        self._config = dict(config)
        self._prompt_editors = {}
        self._workers = []
        self._model_gemini_selecionado = "gemini-2.0-flash"
        self._model_groq_selecionado = "llama-3.3-70b-versatile"
        self._model_openrouter_selecionado = "google/gemini-2.5-flash-preview-05-20"
        self._setup_ui()
        self._carregar_valores()

    def _setup_ui(self) -> None:
        """Configura interface do diálogo."""
        self.setWindowTitle("⚙️ Configurações")
        self.setMinimumSize(700, 600)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # === TABS ===
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._criar_tab_provedores()
        self._criar_tab_processamento()
        self._criar_tab_diretorios()
        self._criar_tab_prompts()

        # === Botões Extras (Import/Export) ===
        extra_layout = QHBoxLayout()
        
        btn_importar = QPushButton("📂 Importar")
        btn_importar.setObjectName("btn_secondary")
        btn_importar.clicked.connect(self._importar_config)
        extra_layout.addWidget(btn_importar)

        btn_exportar = QPushButton("💾 Exportar")
        btn_exportar.setObjectName("btn_secondary")
        btn_exportar.clicked.connect(self._exportar_config)
        extra_layout.addWidget(btn_exportar)
        
        extra_layout.addStretch()
        layout.addLayout(extra_layout)

        # === Botões Principais ===
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_defaults = QPushButton("🔄 Restaurar Padrões")
        btn_defaults.setObjectName("btn_secondary")
        btn_defaults.clicked.connect(self._restaurar_padroes)
        btn_layout.addWidget(btn_defaults)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btn_secondary")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar e Fechar")
        btn_salvar.setObjectName("btn_processar")
        btn_salvar.clicked.connect(self._salvar)
        btn_layout.addWidget(btn_salvar)

        layout.addLayout(btn_layout)

    # ----- Tab 1: IA / Provedores -----

    def _criar_tab_provedores(self) -> None:
        """Aba para selecionar e configurar provedores de IA."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Seleção de Provedor
        grupo_prov = QGroupBox("🤖 Seleção de Provedor")
        prov_layout = QFormLayout(grupo_prov)

        self._combo_provider = QComboBox()
        self._combo_provider.addItems(["Gemini", "Groq", "OpenRouter"])
        self._combo_provider.currentIndexChanged.connect(self._on_provider_changed)
        prov_layout.addRow("Provedor Ativo:", self._combo_provider)

        layout.addWidget(grupo_prov)

        # Stack para configurações específicas
        self._stack_prov = QStackedWidget()
        
        # Página Gemini
        page_gemini = QWidget()
        layout_gemini = QFormLayout(page_gemini)
        
        self._txt_gemini_key = QLineEdit()
        self._txt_gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._txt_gemini_key.setPlaceholderText("Cole sua chave Gemini aqui...")
        layout_gemini.addRow("API Key (Gemini):", self._txt_gemini_key)
        
        self._combo_model_gemini = QComboBox()
        self._combo_model_gemini.setEditable(True)
        layout_gemini.addRow("Modelo:", self._combo_model_gemini)
        
        self._stack_prov.addWidget(page_gemini)

        # Página Groq
        page_groq = QWidget()
        layout_groq = QFormLayout(page_groq)
        
        self._txt_groq_key = QLineEdit()
        self._txt_groq_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._txt_groq_key.setPlaceholderText("Cole sua chave Groq aqui...")
        layout_groq.addRow("API Key (Groq):", self._txt_groq_key)
        
        self._combo_model_groq = QComboBox()
        self._combo_model_groq.setEditable(True)
        layout_groq.addRow("Modelo:", self._combo_model_groq)
        
        self._stack_prov.addWidget(page_groq)

        # Página OpenRouter
        page_openrouter = QWidget()
        layout_openrouter = QFormLayout(page_openrouter)

        self._txt_openrouter_key = QLineEdit()
        self._txt_openrouter_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._txt_openrouter_key.setPlaceholderText("Cole sua chave OpenRouter aqui...")
        layout_openrouter.addRow("API Key (OpenRouter):", self._txt_openrouter_key)

        self._combo_model_openrouter = QComboBox()
        self._combo_model_openrouter.setEditable(True)
        layout_openrouter.addRow("Modelo:", self._combo_model_openrouter)

        self._stack_prov.addWidget(page_openrouter)

        grupo_config = QGroupBox("⚙️ Configuração Específica")
        layout_config = QVBoxLayout(grupo_config)
        layout_config.addWidget(self._stack_prov)
        layout.addWidget(grupo_config)

        # Parâmetros Universais de IA
        grupo_params = QGroupBox("🎛️ Parâmetros da IA")
        params_form = QFormLayout(grupo_params)
        
        self._spin_timeout = QSpinBox()
        self._spin_timeout.setRange(30, 600)
        self._spin_timeout.setSuffix(" seg")
        params_form.addRow("Timeout:", self._spin_timeout)

        self._spin_retries = QSpinBox()
        self._spin_retries.setRange(1, 10)
        params_form.addRow("Tentativas máx.:", self._spin_retries)

        layout.addWidget(grupo_params)
        layout.addStretch()

        self._tabs.addTab(tab, "🤖 IA / Provedores")

    def _on_provider_changed(self, index: int) -> None:
        """Alterna a página de configuração do provedor."""
        self._stack_prov.setCurrentIndex(index)
        provider_map = {0: "gemini", 1: "groq", 2: "openrouter"}
        provider = provider_map.get(index, "gemini")
        key_map = {
            "gemini": self._txt_gemini_key,
            "groq": self._txt_groq_key,
            "openrouter": self._txt_openrouter_key,
        }
        api_key = key_map[provider].text().strip()
        self._buscar_modelos(provider, api_key)

    # ----- Tab 2: Processamento -----

    def _criar_tab_processamento(self) -> None:
        """Aba de parâmetros de processamento."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        grupo_proc = QGroupBox("⚙️ Parâmetros de Revisão")
        proc_form = QFormLayout(grupo_proc)

        self._combo_modo_proc = QComboBox()
        self._combo_modo_proc.addItem(
            "Texto completo (envia o texto estruturado inteiro)", "texto_completo"
        )
        self._combo_modo_proc.addItem(
            "Por seção (divide em seções e revisa cada uma)", "por_secao"
        )
        proc_form.addRow("Modo de análise:", self._combo_modo_proc)

        self._spin_iteracoes = QSpinBox()
        self._spin_iteracoes.setRange(1, 20)
        proc_form.addRow("Iterações máx.:", self._spin_iteracoes)

        self._spin_convergencia = QDoubleSpinBox()
        self._spin_convergencia.setRange(0.5, 1.0)
        self._spin_convergencia.setSingleStep(0.05)
        self._spin_convergencia.setDecimals(2)
        proc_form.addRow("Limiar convergência:", self._spin_convergencia)

        self._spin_temp_rev = QDoubleSpinBox()
        self._spin_temp_rev.setRange(0.0, 1.0)
        self._spin_temp_rev.setSingleStep(0.1)
        self._spin_temp_rev.setDecimals(1)
        proc_form.addRow("Temperatura revisão:", self._spin_temp_rev)

        self._spin_max_tokens = QSpinBox()
        self._spin_max_tokens.setRange(512, 32768)
        self._spin_max_tokens.setSingleStep(512)
        proc_form.addRow("Max tokens:", self._spin_max_tokens)

        layout.addWidget(grupo_proc)

        # Modo Mock
        grupo_mock = QGroupBox("🧪 Modo de Teste")
        mock_form = QFormLayout(grupo_mock)
        self._chk_modo_mock = QCheckBox("Ativar modo mock (sem chamadas à API)")
        mock_form.addRow(self._chk_modo_mock)
        info_mock = QLabel(
            "💡 Quando ativo, gera respostas simuladas sem consumir tokens da API."
        )
        info_mock.setStyleSheet(f"color: {Tema.TEXTO_SECUNDARIO}; font-size: {Tema.FONT_SIZE_SMALL}px;")
        info_mock.setWordWrap(True)
        mock_form.addRow(info_mock)
        layout.addWidget(grupo_mock)
        
        layout.addStretch()
        self._tabs.addTab(tab, "⚡ Processamento")

    # ----- Tab 3: Diretórios -----
    
    def _criar_tab_diretorios(self) -> None:
        """Aba de diretórios."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        grupo_dirs = QGroupBox("📁 Diretórios de Trabalho")
        dirs_layout = QVBoxLayout(grupo_dirs)

        saida_layout = QHBoxLayout()
        saida_layout.addWidget(QLabel("Saída dos relatórios:"))
        self._txt_saida = QLineEdit()
        saida_layout.addWidget(self._txt_saida)
        btn_saida = QPushButton("📁")
        btn_saida.setMaximumWidth(40)
        btn_saida.clicked.connect(lambda: self._selecionar_dir(self._txt_saida))
        saida_layout.addWidget(btn_saida)
        dirs_layout.addLayout(saida_layout)

        dados_layout = QHBoxLayout()
        dados_layout.addWidget(QLabel("Dados persistidos:"))
        self._txt_dados = QLineEdit()
        dados_layout.addWidget(self._txt_dados)
        btn_dados = QPushButton("📁")
        btn_dados.setMaximumWidth(40)
        btn_dados.clicked.connect(lambda: self._selecionar_dir(self._txt_dados))
        dados_layout.addWidget(btn_dados)
        dirs_layout.addLayout(dados_layout)

        layout.addWidget(grupo_dirs)
        layout.addStretch()
        self._tabs.addTab(tab, "📁 Diretórios")

    # ----- Tab 4: Prompts -----

    def _criar_tab_prompts(self) -> None:
        """Aba de edição de prompts."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tabs internas por tipo de prompt
        self._prompt_tabs = QTabWidget()
        self._prompt_tabs.setTabPosition(QTabWidget.TabPosition.West)

        for key, label in PROMPT_LABELS.items():
            editor = QTextEdit()
            editor.setPlaceholderText(f"Prompt para {label}...")
            editor.setStyleSheet(f"font-family: '{Tema.FONT_MONO}'; font-size: {Tema.FONT_SIZE_NORMAL}px;")
            self._prompt_editors[key] = editor
            self._prompt_tabs.addTab(editor, label)

        layout.addWidget(self._prompt_tabs)
        self._tabs.addTab(tab, "📝 Prompts")

    # ----- Carregar / Salvar -----

    def _carregar_valores(self) -> None:
        """Carrega valores da configuração."""
        c = self._config
        api_keys = c.get("api_keys", {})

        # -- Provedores --
        provider_key = c.get("provider", "gemini").lower()
        provider_map = {
            "gemini": "Gemini",
            "groq": "Groq",
            "openrouter": "OpenRouter",
        }
        display_name = provider_map.get(provider_key, "Gemini")
        
        idx_prov = self._combo_provider.findText(display_name)
        if idx_prov >= 0:
            self._combo_provider.setCurrentIndex(idx_prov)
            self._stack_prov.setCurrentIndex(idx_prov)

        # Gemini
        key_gemini = api_keys.get("gemini") or c.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
        self._txt_gemini_key.setText(key_gemini)
        
        self._model_gemini_selecionado = c.get(
            "gemini_model", c.get("model_gemini", "gemini-2.0-flash")
        )

        # Groq
        key_groq = api_keys.get("groq") or os.environ.get("GROQ_API_KEY", "")
        self._txt_groq_key.setText(key_groq)

        self._model_groq_selecionado = c.get(
            "model_groq", "llama-3.3-70b-versatile"
        )

        # OpenRouter
        key_openrouter = api_keys.get("openrouter") or os.environ.get("OPENROUTER_API_KEY", "")
        self._txt_openrouter_key.setText(key_openrouter)

        self._model_openrouter_selecionado = c.get(
            "model_openrouter", "google/gemini-2.5-flash-preview-05-20"
        )

        # Buscar modelos via API para todos os provedores
        self._workers = []  # manter referências
        self._buscar_modelos("gemini", key_gemini)
        self._buscar_modelos("groq", key_groq)
        self._buscar_modelos("openrouter", key_openrouter)

        # -- AI Params --
        self._spin_timeout.setValue(c.get("timeout", 120))
        self._spin_retries.setValue(c.get("max_retries", 3))

        # -- Processamento --
        modo_proc = c.get("modo_processamento", "texto_completo")
        idx_modo = self._combo_modo_proc.findData(modo_proc)
        if idx_modo >= 0:
            self._combo_modo_proc.setCurrentIndex(idx_modo)

        self._spin_iteracoes.setValue(c.get("max_iteracoes", 5))
        self._spin_convergencia.setValue(c.get("limiar_convergencia", 0.95))
        self._spin_temp_rev.setValue(c.get("temperatura_revisao", 0.3))
        self._spin_max_tokens.setValue(c.get("max_tokens_revisao", 4096))
        self._chk_modo_mock.setChecked(c.get("modo_mock", False))
        
        # -- Diretórios --
        self._txt_saida.setText(c.get("diretorio_saida", "./output"))
        self._txt_dados.setText(c.get("diretorio_dados", "./data/textos"))

        # -- Prompts --
        prompts = c.get("prompts", {})
        try:
            from ...infrastructure.ai.prompt_builder import PromptBuilder
            pb = PromptBuilder()
            defaults = pb._templates
        except Exception:
            defaults = {}

        for key, editor in self._prompt_editors.items():
            texto = prompts.get(key, defaults.get(key, ""))
            editor.setPlainText(texto)

    def _buscar_modelos(
        self, provider: str, api_key: str
    ) -> None:
        """Busca modelos via API em background thread."""
        combo_map = {
            "groq": self._combo_model_groq,
            "openrouter": self._combo_model_openrouter,
        }
        combo = combo_map.get(provider, self._combo_model_gemini)
        combo.clear()
        combo.addItem("⏳ Buscando modelos...")
        combo.setEnabled(False)

        worker = _ModelFetchWorker(provider, api_key, parent=self)
        worker.finished.connect(self._on_modelos_recebidos)
        self._workers.append(worker)
        worker.start()

    def closeEvent(self, event) -> None:
        """Aguarda threads terminarem antes de fechar."""
        for w in self._workers:
            if w.isRunning():
                w.wait(3000)  # Espera até 3s
        super().closeEvent(event)

    def _on_modelos_recebidos(
        self, provider: str, modelos: List[str]
    ) -> None:
        """Callback quando modelos são recebidos da API."""
        combo_map = {
            "groq": self._combo_model_groq,
            "openrouter": self._combo_model_openrouter,
        }
        combo = combo_map.get(provider, self._combo_model_gemini)
        modelo_map = {
            "groq": self._model_groq_selecionado,
            "openrouter": self._model_openrouter_selecionado,
        }
        modelo_salvo = modelo_map.get(
            provider, self._model_gemini_selecionado
        )

        combo.clear()
        combo.setEnabled(True)
        combo.setEditable(True)

        if modelos:
            combo.addItems(modelos)
            logger.info(
                f"{provider}: {len(modelos)} modelos carregados"
            )
        else:
            logger.warning(
                f"{provider}: nenhum modelo retornado, usando fallback"
            )

        # Restaurar seleção anterior
        combo.setCurrentText(modelo_salvo)

    def _atualizar_config_from_ui(self) -> None:
        """Atualiza dicionário de config com valores da UI."""
        # Provider
        provider_name = self._combo_provider.currentText().lower()
        self._config["provider"] = provider_name
        
        # API Keys
        api_keys = self._config.get("api_keys", {})
        api_keys["gemini"] = self._txt_gemini_key.text().strip()
        api_keys["groq"] = self._txt_groq_key.text().strip()
        api_keys["openrouter"] = self._txt_openrouter_key.text().strip()
        self._config["api_keys"] = api_keys
        
        # Manter compatibililidade com env vars
        if api_keys["gemini"]:
            self._config["gemini_api_key"] = api_keys["gemini"]

        # Models
        self._config["model_gemini"] = self._combo_model_gemini.currentText()
        self._config["gemini_model"] = self._config["model_gemini"] # Retrocompatibilidade
        self._config["model_groq"] = self._combo_model_groq.currentText()
        self._config["model_openrouter"] = self._combo_model_openrouter.currentText()

        # Params
        self._config.update({
            "timeout": self._spin_timeout.value(),
            "max_retries": self._spin_retries.value(),
            "modo_processamento": self._combo_modo_proc.currentData(),
            "max_iteracoes": self._spin_iteracoes.value(),
            "limiar_convergencia": self._spin_convergencia.value(),
            "temperatura_revisao": self._spin_temp_rev.value(),
            "max_tokens_revisao": self._spin_max_tokens.value(),
            "modo_mock": self._chk_modo_mock.isChecked(),
            "diretorio_saida": self._txt_saida.text(),
            "diretorio_dados": self._txt_dados.text(),
        })

        # Prompts
        prompts = {}
        for key, editor in self._prompt_editors.items():
            texto = editor.toPlainText().strip()
            if texto:
                prompts[key] = texto
        if prompts:
            self._config["prompts"] = prompts

    def _selecionar_dir(self, campo: QLineEdit) -> None:
        """Abre seletor de diretório."""
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Diretório")
        if dir_path:
            campo.setText(dir_path)

    def _restaurar_padroes(self) -> None:
        """Restaura prompts e configs padrão."""
        resp = QMessageBox.question(
            self,
            "Restaurar Padrões",
            "Restaurar configurações e prompts para valores originais?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            # Restaurar prompts
            try:
                from ...infrastructure.ai.prompt_builder import PromptBuilder
                pb = PromptBuilder()
                for key, editor in self._prompt_editors.items():
                    default = pb._templates.get(key, "")
                    editor.setPlainText(default)
            except Exception:
                pass

    def _salvar(self) -> None:
        """Salva configurações."""
        self._atualizar_config_from_ui()
        
        # Atualizar env vars para sessão atual
        api_keys = self._config.get("api_keys", {})
        if api_keys.get("gemini"):
            os.environ["GEMINI_API_KEY"] = api_keys["gemini"]
        if api_keys.get("groq"):
            os.environ["GROQ_API_KEY"] = api_keys["groq"]
            
        self.accept()

    def _importar_config(self) -> None:
        """Importa configuração de JSON."""
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Importar Configuração", "", "JSON Files (*.json)"
        )
        if caminho:
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    nova = json.load(f)
                self._config.update(nova)
                self._carregar_valores()
                QMessageBox.information(self, "Sucesso", "Configuração importada!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao importar: {e}")

    def _exportar_config(self) -> None:
        """Exporta configuração para JSON."""
        self._atualizar_config_from_ui()
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Exportar Configuração", "config_backup.json", "JSON Files (*.json)"
        )
        if caminho:
            try:
                with open(caminho, "w", encoding="utf-8") as f:
                    json.dump(self._config, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Sucesso", "Configuração exportada!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar: {e}")

    def obter_config(self) -> dict:
        return dict(self._config)
