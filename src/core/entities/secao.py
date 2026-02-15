"""
Módulo contendo a entidade Seção.

Define a estrutura de uma seção de texto, incluindo
conteúdo original, configurações de revisão e histórico.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..enums.status_texto import StatusTexto
from ..exceptions.secao_exceptions import (
    SecaoInvalidaException,
    RevisaoNaoEncontradaException,
)
from .revisao import Revisao
from .erro import Erro


@dataclass
class Secao:
    """
    Representa uma seção de um texto estruturado.

    Uma seção é uma divisão lógica do texto (ex: Introdução,
    Metodologia, Conclusões) revisada de forma independente
    pelos agentes de IA.

    Attributes:
        titulo: Título da seção conforme identificado no PDF
        conteudo_original: Texto original extraído do PDF
        numero_pagina_inicio: Primeira página (baseado em 1)
        numero_pagina_fim: Última página (baseado em 1)
        nivel_hierarquico: Nível (1=principal, 2=sub, etc.)
        configuracao_id: ID da configuração de revisão
        revisoes: Histórico completo de revisões
        status: Status atual da revisão desta seção
        data_criacao: Data e hora de criação
        metadados: Metadados adicionais

    Example:
        >>> secao = Secao(
        ...     titulo="1. INTRODUÇÃO",
        ...     conteudo_original="Este texto tem...",
        ...     numero_pagina_inicio=1,
        ...     numero_pagina_fim=3,
        ... )
    """

    titulo: str
    conteudo_original: str
    numero_pagina_inicio: int
    numero_pagina_fim: int
    nivel_hierarquico: int = 1
    configuracao_id: Optional[str] = None
    revisoes: List[Revisao] = field(
        default_factory=list
    )
    status: StatusTexto = StatusTexto.PENDENTE
    data_criacao: datetime = field(
        default_factory=datetime.now
    )
    metadados: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Validações após criação da instância."""
        self._validar_secao()

    def _validar_secao(self) -> None:
        """
        Valida os dados da seção.

        Raises:
            SecaoInvalidaException: Se validações falharem
        """
        if not self.titulo or not self.titulo.strip():
            raise SecaoInvalidaException(
                "Título da seção não pode ser vazio"
            )
        if (
            not self.conteudo_original
            or not self.conteudo_original.strip()
        ):
            raise SecaoInvalidaException(
                "Conteúdo da seção não pode ser vazio"
            )
        if self.numero_pagina_inicio < 1:
            raise SecaoInvalidaException(
                "Número de página inicial deve ser >= 1"
            )
        if (
            self.numero_pagina_fim
            < self.numero_pagina_inicio
        ):
            raise SecaoInvalidaException(
                "Página final deve ser >= página inicial"
            )
        if self.nivel_hierarquico < 1:
            raise SecaoInvalidaException(
                "Nível hierárquico deve ser >= 1"
            )

    def adicionar_revisao(
        self, revisao: Revisao
    ) -> None:
        """
        Adiciona uma nova revisão ao histórico.

        Args:
            revisao: Objeto Revisao a ser adicionado

        Raises:
            ValueError: Se revisão for None
        """
        if revisao is None:
            raise ValueError(
                "Revisão não pode ser None"
            )
        self.revisoes.append(revisao)
        if revisao.convergiu:
            self.status = StatusTexto.CONCLUIDO

    def obter_ultima_revisao(
        self,
    ) -> Optional[Revisao]:
        """
        Retorna a revisão mais recente.

        Returns:
            Última Revisao ou None se não houver
        """
        return self.revisoes[-1] if self.revisoes else None

    def obter_revisao_por_indice(
        self, indice: int
    ) -> Revisao:
        """
        Retorna revisão pelo índice.

        Args:
            indice: Índice da revisão (0-based)

        Returns:
            Objeto Revisao

        Raises:
            RevisaoNaoEncontradaException: Se inválido
        """
        if indice < 0 or indice >= len(self.revisoes):
            raise RevisaoNaoEncontradaException(
                f"Índice de revisão inválido: {indice}"
            )
        return self.revisoes[indice]

    def obter_todos_erros(self) -> List[Erro]:
        """
        Retorna todos os erros únicos identificados em todas as revisões.
        
        Realiza deduplicação baseada no trecho original e tipo do erro.
        Isso consolida o histórico de correções sem repetir erros persistentes.

        Returns:
            Lista de erros únicos identificados
        """
        todos_erros = []
        unicos = set()
        
        for revisao in self.revisoes:
            for erro in revisao.erros:
                # Chave de unicidade: tipo + trecho
                # Normalizar trecho removendo espaços extras
                trecho_norm = " ".join(erro.trecho_original.split())
                chave = (erro.tipo.value, trecho_norm)
                
                if chave not in unicos:
                    unicos.add(chave)
                    todos_erros.append(erro)
                    
        return todos_erros

    def obter_erros_por_tipo(
        self, tipo_erro: str
    ) -> List[Erro]:
        """
        Filtra erros por tipo na última revisão.

        Args:
            tipo_erro: Tipo de erro a filtrar

        Returns:
            Lista de erros do tipo especificado
        """
        todos = self.obter_todos_erros()
        return [
            e for e in todos
            if e.tipo.value == tipo_erro
        ]

    @property
    def numero_paginas(self) -> int:
        """Total de páginas da seção."""
        return (
            self.numero_pagina_fim
            - self.numero_pagina_inicio
            + 1
        )

    @property
    def tamanho_conteudo(self) -> int:
        """Tamanho do conteúdo em caracteres."""
        return len(self.conteudo_original)

    @property
    def numero_palavras(self) -> int:
        """Número aproximado de palavras."""
        return len(self.conteudo_original.split())

    @property
    def foi_revisada(self) -> bool:
        """Verifica se já passou por alguma revisão."""
        return len(self.revisoes) > 0

    @property
    def esta_concluida(self) -> bool:
        """Verifica se a revisão está concluída."""
        return self.status == StatusTexto.CONCLUIDO

    @property
    def total_iteracoes(self) -> int:
        """Número total de revisões realizadas."""
        return len(self.revisoes)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário."""
        return {
            "titulo": self.titulo,
            "conteudo_original": self.conteudo_original,
            "numero_pagina_inicio": (
                self.numero_pagina_inicio
            ),
            "numero_pagina_fim": self.numero_pagina_fim,
            "nivel_hierarquico": self.nivel_hierarquico,
            "configuracao_id": self.configuracao_id,
            "revisoes": [
                r.to_dict() for r in self.revisoes
            ],
            "status": self.status.value,
            "data_criacao": (
                self.data_criacao.isoformat()
            ),
            "metadados": self.metadados,
        }

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any]
    ) -> "Secao":
        """
        Cria instância a partir de dicionário.

        Args:
            data: Dicionário com dados da seção

        Returns:
            Nova instância de Secao
        """
        secao = cls(
            titulo=data["titulo"],
            conteudo_original=data["conteudo_original"],
            numero_pagina_inicio=data[
                "numero_pagina_inicio"
            ],
            numero_pagina_fim=data[
                "numero_pagina_fim"
            ],
            nivel_hierarquico=data.get(
                "nivel_hierarquico", 1
            ),
            configuracao_id=data.get("configuracao_id"),
            status=StatusTexto(
                data.get("status", "pendente")
            ),
            metadados=data.get("metadados", {}),
        )
        for rev_data in data.get("revisoes", []):
            secao.adicionar_revisao(
                Revisao.from_dict(rev_data)
            )
        return secao

    def __str__(self) -> str:
        """Representação legível."""
        return (
            f"Secao({self.titulo}, "
            f"pp.{self.numero_pagina_inicio}"
            f"-{self.numero_pagina_fim}, "
            f"{len(self.revisoes)} rev.)"
        )
