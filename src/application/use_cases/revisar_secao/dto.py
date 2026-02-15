"""
DTOs do caso de uso RevisarSecao.

Define objetos de transferência de dados para
a revisão de seções individuais.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class RevisarSecaoInputDTO:
    """
    DTO de entrada para revisão de seção.

    Attributes:
        titulo_secao: Título da seção a revisar
        conteudo: Conteúdo textual da seção
        configuracao_id: ID da configuração de revisão
        max_iteracoes: Número máximo de iterações
        limiar_convergencia: Limiar para convergência
    """

    titulo_secao: str
    conteudo: str
    configuracao_id: str = "padrao"
    max_iteracoes: int = 5
    limiar_convergencia: float = 0.95


@dataclass
class RevisarSecaoOutputDTO:
    """
    DTO de saída da revisão de seção.

    Attributes:
        titulo_secao: Título da seção revisada
        total_erros: Total de erros encontrados
        total_iteracoes: Número de iterações realizadas
        convergiu: Se a revisão convergiu
        erros_por_tipo: Contagem de erros por tipo
        texto_revisado: Texto final após revisão
        sucesso: Se a revisão foi bem-sucedida
    """

    titulo_secao: str = ""
    total_erros: int = 0
    total_iteracoes: int = 0
    convergiu: bool = False
    erros_por_tipo: Dict[str, int] = field(
        default_factory=dict
    )
    texto_revisado: str = ""
    sucesso: bool = True
