"""
Módulo contendo a entidade Erro.

Define a estrutura de um erro identificado durante
a revisão de uma seção do texto estruturado.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from ..enums.tipo_erro import TipoErro
from ..value_objects.localizacao_erro import LocalizacaoErro


@dataclass
class Erro:
    """
    Representa um erro identificado no texto.

    Cada erro contém informações sobre o tipo, localização,
    trecho original com problema e a correção sugerida.

    Attributes:
        tipo: Categoria do erro identificado
        descricao: Descrição detalhada do erro
        trecho_original: Texto original com o erro
        sugestao_correcao: Correção proposta pelo agente
        localizacao: Localização precisa no documento
        severidade: Nível de severidade (1=baixa, 5=crítica)
        confianca: Grau de confiança da detecção (0.0-1.0)
        agente_origem: Nome do agente que detectou o erro
        data_deteccao: Data/hora da detecção
        aceito: Se a correção foi aceita pelo usuário
        justificativa: Justificativa técnica para o erro

    Example:
        >>> erro = Erro(
        ...     tipo=TipoErro.GRAMATICAL,
        ...     descricao="Concordância verbal incorreta",
        ...     trecho_original="os dados foi analisados",
        ...     sugestao_correcao="os dados foram analisados",
        ...     severidade=3
        ... )
    """

    tipo: TipoErro
    descricao: str
    trecho_original: str
    sugestao_correcao: str
    localizacao: Optional[LocalizacaoErro] = None
    severidade: int = 1
    confianca: float = 1.0
    agente_origem: str = ""
    data_deteccao: datetime = field(
        default_factory=datetime.now
    )
    aceito: Optional[bool] = None
    justificativa: str = ""

    def __post_init__(self) -> None:
        """Valida os dados do erro."""
        if not self.descricao or not self.descricao.strip():
            raise ValueError(
                "Descrição do erro não pode ser vazia"
            )
        if self.severidade < 1 or self.severidade > 5:
            raise ValueError(
                "Severidade deve estar entre 1 e 5"
            )
        if self.confianca < 0.0 or self.confianca > 1.0:
            raise ValueError(
                "Confiança deve estar entre 0.0 e 1.0"
            )

    def aceitar(self) -> None:
        """Marca a correção como aceita."""
        self.aceito = True

    def rejeitar(self) -> None:
        """Marca a correção como rejeitada."""
        self.aceito = False

    @property
    def esta_pendente(self) -> bool:
        """Verifica se a correção ainda não foi avaliada."""
        return self.aceito is None

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário."""
        return {
            "tipo": self.tipo.value,
            "descricao": self.descricao,
            "trecho_original": self.trecho_original,
            "sugestao_correcao": self.sugestao_correcao,
            "localizacao": (
                self.localizacao.to_dict()
                if self.localizacao
                else None
            ),
            "severidade": self.severidade,
            "confianca": self.confianca,
            "agente_origem": self.agente_origem,
            "data_deteccao": (
                self.data_deteccao.isoformat()
            ),
            "aceito": self.aceito,
            "justificativa": self.justificativa,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Erro":
        """
        Cria instância a partir de dicionário.

        Args:
            data: Dicionário com dados do erro

        Returns:
            Nova instância de Erro
        """
        localizacao = None
        if data.get("localizacao"):
            loc = data["localizacao"]
            localizacao = LocalizacaoErro(
                pagina=loc["pagina"],
                paragrafo=loc.get("paragrafo", 0),
                linha=loc.get("linha", 0),
                posicao_inicio=loc.get(
                    "posicao_inicio", 0
                ),
                posicao_fim=loc.get("posicao_fim", 0),
                contexto=loc.get("contexto"),
            )

        return cls(
            tipo=TipoErro(data["tipo"]),
            descricao=data["descricao"],
            trecho_original=data["trecho_original"],
            sugestao_correcao=data["sugestao_correcao"],
            localizacao=localizacao,
            severidade=data.get("severidade", 1),
            confianca=data.get("confianca", 1.0),
            agente_origem=data.get("agente_origem", ""),
            aceito=data.get("aceito"),
            justificativa=data.get("justificativa", ""),
        )

    def __str__(self) -> str:
        """Representação legível."""
        return (
            f"Erro({self.tipo.value}: "
            f"{self.descricao[:50]}...)"
        )
