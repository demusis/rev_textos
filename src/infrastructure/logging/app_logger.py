"""
Sistema de logging estruturado.

Implementação concreta do ILogger usando o módulo
logging padrão do Python com formatação customizada.
"""

import logging
import sys
from pathlib import Path
from typing import Any

from ...core.interfaces.services.i_logger import (
    ILogger,
)


class AppLogger(ILogger):
    """
    Logger concreto usando módulo logging do Python.

    Configura logging para arquivo e console com
    formatação em PT-BR e níveis configuráveis.
    """

    def __init__(
        self,
        nome: str = "revisor_textos",
        nivel: str = "INFO",
        diretorio_log: str = "./logs",
    ) -> None:
        """
        Inicializa o logger.

        Args:
            nome: Nome do logger
            nivel: Nível de logging
            diretorio_log: Diretório para arquivos
        """
        self._logger = logging.getLogger(nome)
        self._logger.setLevel(
            getattr(logging, nivel.upper(), logging.INFO)
        )

        # Evitar duplicação de handlers
        if not self._logger.handlers:
            self._configurar_handlers(
                diretorio_log
            )

    def _configurar_handlers(
        self, diretorio_log: str
    ) -> None:
        """Configura handlers de console e arquivo."""
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(formato)
        self._logger.addHandler(console)

        # File handler
        try:
            log_dir = Path(diretorio_log)
            log_dir.mkdir(
                parents=True, exist_ok=True
            )
            arquivo = logging.FileHandler(
                log_dir / "revisor_textos.log",
                encoding="utf-8",
            )
            arquivo.setLevel(logging.DEBUG)
            arquivo.setFormatter(formato)
            self._logger.addHandler(arquivo)
        except Exception as e:
            self._logger.warning(
                f"Não foi possível criar log "
                f"em arquivo: {e}"
            )

    def debug(
        self, mensagem: str, **kwargs: Any
    ) -> None:
        self._logger.debug(
            mensagem, extra=kwargs
        )

    def info(
        self, mensagem: str, **kwargs: Any
    ) -> None:
        self._logger.info(
            mensagem, extra=kwargs
        )

    def warning(
        self, mensagem: str, **kwargs: Any
    ) -> None:
        self._logger.warning(
            mensagem, extra=kwargs
        )

    def error(
        self, mensagem: str, **kwargs: Any
    ) -> None:
        self._logger.error(
            mensagem, extra=kwargs
        )

    def critical(
        self, mensagem: str, **kwargs: Any
    ) -> None:
        self._logger.critical(
            mensagem, extra=kwargs
        )
