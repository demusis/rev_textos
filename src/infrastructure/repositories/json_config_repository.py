"""
Repositório de configurações.

Implementação concreta usando JSON para persistência
de configurações e prompts customizados.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ...core.interfaces.repositories.i_config_repository import (
    IConfigRepository,
)

logger = logging.getLogger(__name__)

# Configuração padrão do sistema
CONFIG_PADRAO: Dict[str, Any] = {
    "gemini_model": "gemini-2.0-flash",
    "max_retries": 3,
    "timeout": 120,
    "requests_per_minute": 60,
    "temperatura_revisao": 0.3,
    "temperatura_validacao": 0.2,
    "max_iteracoes": 5,
    "limiar_convergencia": 0.95,
    "max_tokens_revisao": 4096,
    "diretorio_saida": "./output",
    "diretorio_dados": "./data",
    "formatos_relatorio": ["markdown", "html"],
    "logging_level": "INFO",
    "provider": "gemini",
    "api_keys": {
        "gemini": "",
        "groq": "",
        "huggingface": "",
        "ollama": "",
    },
    "model_gemini": "gemini-2.0-flash",
    "model_groq": "llama3-70b-8192",
    "timeout_groq": 60,
}


class JsonConfigRepository(IConfigRepository):
    """
    Repositório de configurações em JSON.

    Carrega e persiste configurações do sistema
    em arquivo JSON com fallback para defaults.
    """

    def __init__(
        self,
        caminho_config: str = "./config/settings.json",
        caminho_prompts: str = "./config/prompts",
    ) -> None:
        """
        Inicializa o repositório de configurações.

        Args:
            caminho_config: Caminho do arquivo config
            caminho_prompts: Diretório de prompts
        """
        self._caminho_config = Path(caminho_config)
        self._caminho_prompts = Path(caminho_prompts)
        self._config: Dict[str, Any] = {}
        self._carregar_ou_criar()

    def _carregar_ou_criar(self) -> None:
        """Carrega config existente ou cria default."""
        if self._caminho_config.exists():
            try:
                self._config = json.loads(
                    self._caminho_config.read_text(
                        encoding="utf-8"
                    )
                )
                logger.info("Configuração carregada")
                return
            except Exception as e:
                logger.warning(
                    f"Erro ao carregar config: {e}. "
                    f"Usando defaults."
                )

        self._config = dict(CONFIG_PADRAO)
        self.salvar_configuracao(self._config)

    def carregar_configuracao(
        self,
    ) -> Dict[str, Any]:
        """Retorna configuração completa."""
        return dict(self._config)

    def salvar_configuracao(
        self, config: Dict[str, Any]
    ) -> None:
        """Salva configuração em disco."""
        self._config = dict(config)
        self._caminho_config.parent.mkdir(
            parents=True, exist_ok=True
        )
        self._caminho_config.write_text(
            json.dumps(
                config,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        logger.info("Configuração salva")

    def obter_valor(
        self, chave: str, padrao: Any = None
    ) -> Any:
        """Obtém valor por chave (dot notation)."""
        partes = chave.split(".")
        valor = self._config
        for parte in partes:
            if isinstance(valor, dict):
                valor = valor.get(parte)
            else:
                return padrao
            if valor is None:
                return padrao
        return valor

    def definir_valor(
        self, chave: str, valor: Any
    ) -> None:
        """Define valor por chave."""
        partes = chave.split(".")
        config = self._config
        for parte in partes[:-1]:
            if parte not in config:
                config[parte] = {}
            config = config[parte]
        config[partes[-1]] = valor
        self.salvar_configuracao(self._config)

    def carregar_prompt(
        self, tipo: str
    ) -> Optional[Dict[str, Any]]:
        """Carrega template de prompt por tipo."""
        caminho = (
            self._caminho_prompts / f"{tipo}.json"
        )
        if caminho.exists():
            try:
                return json.loads(
                    caminho.read_text(
                        encoding="utf-8"
                    )
                )
            except Exception as e:
                logger.warning(
                    f"Erro ao carregar prompt "
                    f"'{tipo}': {e}"
                )

        return None
