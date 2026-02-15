"""Enumerações do domínio do sistema de revisão de textos."""

from .status_texto import StatusTexto
from .tipo_erro import TipoErro
from .tipo_agente import TipoAgente
from .formato_relatorio import FormatoRelatorio

__all__ = [
    "StatusTexto",
    "TipoErro",
    "TipoAgente",
    "FormatoRelatorio",
]
