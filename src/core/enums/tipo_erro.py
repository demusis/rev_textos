"""
Módulo de enumeração de tipos de erro.

Define as categorias de erros que podem ser identificados
durante a revisão de um texto estruturado.
"""

from enum import Enum


class TipoErro(Enum):
    """
    Enumeração dos tipos de erros identificáveis.

    Categoriza os erros encontrados durante a revisão
    para facilitar filtragem e priorização.

    Attributes:
        GRAMATICAL: Erros de gramática e ortografia
        TECNICO: Erros técnicos/científicos no conteúdo
        JURIDICO: Erros em terminologia ou procedimentos jurídicos
        FORMATACAO: Erros de formatação e estrutura
        CONSISTENCIA: Inconsistências entre seções
        REFERENCIA: Erros em referências ou citações
        NUMERICO: Erros em valores numéricos ou cálculos
        LOGICO: Erros de lógica ou raciocínio
        OMISSAO: Informações faltantes ou incompletas
        OUTRO: Outros tipos não categorizados
    """

    GRAMATICAL = "gramatical"
    TECNICO = "tecnico"
    JURIDICO = "juridico"
    FORMATACAO = "formatacao"
    CONSISTENCIA = "consistencia"
    REFERENCIA = "referencia"
    NUMERICO = "numerico"
    LOGICO = "logico"
    OMISSAO = "omissao"
    OUTRO = "outro"

    def __str__(self) -> str:
        """Retorna representação legível do tipo."""
        return self.value

    @property
    def descricao(self) -> str:
        """Retorna descrição detalhada do tipo de erro."""
        descricoes = {
            TipoErro.GRAMATICAL: "Erro gramatical ou ortográfico",
            TipoErro.TECNICO: "Erro técnico ou científico",
            TipoErro.JURIDICO: "Erro jurídico ou processual",
            TipoErro.FORMATACAO: "Erro de formatação",
            TipoErro.CONSISTENCIA: "Inconsistência entre seções",
            TipoErro.REFERENCIA: "Erro em referência ou citação",
            TipoErro.NUMERICO: "Erro numérico ou de cálculo",
            TipoErro.LOGICO: "Erro de lógica ou raciocínio",
            TipoErro.OMISSAO: "Informação omitida ou incompleta",
            TipoErro.OUTRO: "Outro tipo de erro",
        }
        return descricoes.get(self, "Tipo desconhecido")
