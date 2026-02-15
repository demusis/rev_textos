"""
Módulo de enumeração de status do texto.

Define os possíveis estados de um texto ou seção durante
o ciclo de vida do processamento.
"""

from enum import Enum


class StatusTexto(Enum):
    """
    Enumeração dos possíveis status de um texto ou seção.

    Representa o ciclo de vida completo do processamento,
    desde o carregamento até a conclusão ou erro.

    Attributes:
        PENDENTE: Aguardando início do processamento
        PROCESSANDO: Em processamento ativo
        REVISANDO: Em revisão por agentes de IA
        VALIDANDO: Em validação de consistência
        CONCLUIDO: Processamento finalizado com sucesso
        ERRO: Processamento finalizado com erro
        CANCELADO: Processamento cancelado pelo usuário
        PAUSADO: Processamento pausado temporariamente
    """

    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    REVISANDO = "revisando"
    VALIDANDO = "validando"
    CONCLUIDO = "concluido"
    ERRO = "erro"
    CANCELADO = "cancelado"
    PAUSADO = "pausado"

    def __str__(self) -> str:
        """Retorna representação legível do status."""
        return self.value

    @property
    def esta_ativo(self) -> bool:
        """Verifica se o status indica processamento ativo."""
        return self in (
            StatusTexto.PROCESSANDO,
            StatusTexto.REVISANDO,
            StatusTexto.VALIDANDO,
        )

    @property
    def esta_finalizado(self) -> bool:
        """Verifica se o status indica fim do processamento."""
        return self in (
            StatusTexto.CONCLUIDO,
            StatusTexto.ERRO,
            StatusTexto.CANCELADO,
        )
