"""Entidades do domínio do sistema de revisão de textos."""

from .texto_estruturado import TextoEstruturado
from .secao import Secao
from .revisao import Revisao
from .erro import Erro
from .correcao import Correcao
from .relatorio import Relatorio

__all__ = [
    "TextoEstruturado",
    "Secao",
    "Revisao",
    "Erro",
    "Correcao",
    "Relatorio",
]
