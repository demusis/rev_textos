"""
Sistema de logging estruturado.

Implementação concreta do ILogger usando o módulo
logging padrão do Python com formatação customizada.
Inclui handler Qt para exibição em GUI.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ...core.interfaces.services.i_logger import (
    ILogger,
)

class LogSignalEmitter(QObject):
    """Emissor de sinal Qt para mensagens de log.

    Ponte thread-safe entre logging.Handler e a GUI.
    O sinal carrega (nível, mensagem formatada).
    """
    log_message = pyqtSignal(str, str)


class QtLogHandler(logging.Handler):
    """Handler de logging que emite via sinal Qt.

    Permite que a GUI receba as mesmas mensagens
    detalhadas exibidas no terminal.
    """

    def __init__(
        self,
        emitter: LogSignalEmitter,
        level: int = logging.INFO,
    ) -> None:
        super().__init__(level)
        self._emitter = emitter

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._emitter.log_message.emit(
                record.levelname, msg
            )
        except Exception:
            self.handleError(record)


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

        # Emissor Qt para GUI
        self._log_emitter = LogSignalEmitter()

        # Evitar duplicação de handlers
        if not self._logger.handlers:
            self._configurar_handlers(
                diretorio_log
            )

        # Propagar formatação para todos os loggers
        # do namespace 'src' (gateways, agentes, etc.)
        self._configurar_namespace_src()

    def _configurar_handlers(
        self, diretorio_log: str
    ) -> None:
        """Configura handlers de console e arquivo."""
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Formato idêntico ao terminal para a GUI
        formato_gui = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(formato)
        self._logger.addHandler(console)

        # Qt GUI handler
        qt_handler = QtLogHandler(
            self._log_emitter, logging.INFO
        )
        qt_handler.setFormatter(formato_gui)
        self._logger.addHandler(qt_handler)

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

    def _configurar_namespace_src(self) -> None:
        """Propaga handlers para o namespace 'src'.

        Garante que loggers module-level como
        logging.getLogger('src.infrastructure.ai.gemini_gateway')
        herdem a mesma formatação do AppLogger.
        """
        root_src = logging.getLogger("src")
        if not root_src.handlers:
            root_src.setLevel(logging.DEBUG)
            root_src.propagate = False
            for h in self._logger.handlers:
                root_src.addHandler(h)

    @property
    def log_emitter(self) -> LogSignalEmitter:
        """Retorna o emissor de sinais para a GUI."""
        return self._log_emitter

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
