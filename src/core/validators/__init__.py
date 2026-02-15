"""Validadores do domínio do sistema de revisão de textos."""

from .texto_validator import TextoValidator
from .secao_validator import SecaoValidator
from .config_validator import ConfigValidator

__all__ = [
    "TextoValidator",
    "SecaoValidator",
    "ConfigValidator",
]
