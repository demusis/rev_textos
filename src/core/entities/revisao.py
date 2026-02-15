"""
Módulo contendo a entidade Revisão.

Define a estrutura de uma iteração de revisão realizada
por um agente de IA sobre uma seção do texto.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

from .erro import Erro
from .correcao import Correcao


@dataclass
class Revisao:
    """
    Representa uma iteração de revisão de uma seção.

    Cada revisão contém os erros encontrados, correções
    propostas e metadados sobre o processamento realizado.

    Attributes:
        numero_iteracao: Número sequencial da iteração
        texto_entrada: Texto enviado para revisão
        texto_saida: Texto retornado pelo agente
        erros: Lista de erros identificados
        correcoes: Lista de correções propostas
        agente: Nome do agente que realizou a revisão
        convergiu: Se esta iteração atingiu convergência
        tokens_input: Tokens de entrada consumidos
        tokens_output: Tokens de saída consumidos
        tempo_processamento_seg: Tempo de processamento
        data_inicio: Data/hora de início
        data_fim: Data/hora de conclusão
        resposta_bruta: Resposta bruta da API (debug)
        prompt_utilizado: Prompt utilizado (debug)

    Example:
        >>> revisao = Revisao(
        ...     numero_iteracao=1,
        ...     texto_entrada="Texto original...",
        ...     texto_saida="Texto revisado...",
        ...     agente="revisor"
        ... )
    """

    numero_iteracao: int
    texto_entrada: str
    texto_saida: str = ""
    erros: List[Erro] = field(default_factory=list)
    correcoes: List[Correcao] = field(
        default_factory=list
    )
    agente: str = ""
    convergiu: bool = False
    tokens_input: int = 0
    tokens_output: int = 0
    tempo_processamento_seg: float = 0.0
    data_inicio: datetime = field(
        default_factory=datetime.now
    )
    data_fim: Optional[datetime] = None
    resposta_bruta: str = ""
    prompt_utilizado: str = ""

    def adicionar_erro(self, erro: Erro) -> None:
        """
        Adiciona um erro encontrado nesta revisão.

        Args:
            erro: Erro identificado pelo agente

        Raises:
            ValueError: Se erro for None
        """
        if erro is None:
            raise ValueError("Erro não pode ser None")
        self.erros.append(erro)

    def adicionar_correcao(
        self, correcao: Correcao
    ) -> None:
        """
        Adiciona uma correção proposta nesta revisão.

        Args:
            correcao: Correção proposta pelo agente

        Raises:
            ValueError: Se correção for None
        """
        if correcao is None:
            raise ValueError(
                "Correção não pode ser None"
            )
        self.correcoes.append(correcao)

    def finalizar(self) -> None:
        """Marca a revisão como finalizada."""
        self.data_fim = datetime.now()
        if self.data_inicio:
            delta = self.data_fim - self.data_inicio
            self.tempo_processamento_seg = (
                delta.total_seconds()
            )

    @property
    def total_erros(self) -> int:
        """Retorna o total de erros encontrados."""
        return len(self.erros)

    @property
    def total_correcoes(self) -> int:
        """Retorna o total de correções propostas."""
        return len(self.correcoes)

    @property
    def total_tokens(self) -> int:
        """Retorna o total de tokens consumidos."""
        return self.tokens_input + self.tokens_output

    @property
    def esta_finalizada(self) -> bool:
        """Verifica se a revisão foi finalizada."""
        return self.data_fim is not None

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário."""
        return {
            "numero_iteracao": self.numero_iteracao,
            "texto_entrada": self.texto_entrada,
            "texto_saida": self.texto_saida,
            "erros": [e.to_dict() for e in self.erros],
            "correcoes": [
                c.to_dict() for c in self.correcoes
            ],
            "agente": self.agente,
            "convergiu": self.convergiu,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "tempo_processamento_seg": (
                self.tempo_processamento_seg
            ),
            "data_inicio": self.data_inicio.isoformat(),
            "data_fim": (
                self.data_fim.isoformat()
                if self.data_fim
                else None
            ),
        }

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any]
    ) -> "Revisao":
        """
        Cria instância a partir de dicionário.

        Args:
            data: Dicionário com dados da revisão

        Returns:
            Nova instância de Revisao
        """
        revisao = cls(
            numero_iteracao=data["numero_iteracao"],
            texto_entrada=data["texto_entrada"],
            texto_saida=data.get("texto_saida", ""),
            agente=data.get("agente", ""),
            convergiu=data.get("convergiu", False),
            tokens_input=data.get("tokens_input", 0),
            tokens_output=data.get("tokens_output", 0),
            tempo_processamento_seg=data.get(
                "tempo_processamento_seg", 0.0
            ),
        )

        for erro_data in data.get("erros", []):
            revisao.adicionar_erro(
                Erro.from_dict(erro_data)
            )

        for corr_data in data.get("correcoes", []):
            revisao.adicionar_correcao(
                Correcao.from_dict(corr_data)
            )

        return revisao

    def __str__(self) -> str:
        """Representação legível."""
        status = "convergiu" if self.convergiu else "aberta"
        return (
            f"Revisão #{self.numero_iteracao} "
            f"({status}, {self.total_erros} erros)"
        )
