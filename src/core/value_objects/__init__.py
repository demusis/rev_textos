"""Value Objects do domínio do sistema de revisão de textos."""

from .localizacao_erro import LocalizacaoErro
from .metadados_pdf import MetadadosPDF
from .metricas_revisao import MetricasRevisao

__all__ = [
    "LocalizacaoErro",
    "MetadadosPDF",
    "MetricasRevisao",
]
