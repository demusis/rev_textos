"""
Módulo contendo a entidade TextoEstruturado.

Define a estrutura principal de um texto estruturado,
o agregado raiz do domínio.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib

from ..enums.status_texto import StatusTexto
from ..value_objects.metadados_pdf import MetadadosPDF
from ..exceptions.texto_exceptions import (
    TextoInvalidoException,
    SecaoNaoEncontradaException,
    SecaoDuplicadaException,
)
from .secao import Secao


@dataclass
class TextoEstruturado:
    """
    Representa um texto estruturado completo.

    Agregado raiz do domínio, contendo todas as informações
    do texto, suas seções, revisões e metadados.

    Attributes:
        caminho_arquivo: Caminho absoluto do arquivo original
        nome_arquivo: Nome do arquivo (ex: "texto_001.pdf")
        data_carregamento: Data/hora do carregamento
        data_ultima_modificacao: Última modificação do arquivo
        status: Status atual do processamento
        secoes: Lista ordenada de seções identificadas
        metadados: Metadados extraídos (se aplicável)
        hash_arquivo: Hash SHA-256 do arquivo
        tamanho_bytes: Tamanho em bytes
        numero_paginas: Total de páginas (se aplicável)
        historico: Eventos de processamento

    Example:
        >>> texto = TextoEstruturado(
        ...     caminho_arquivo="/dados/texto.pdf",
        ...     nome_arquivo="texto.pdf",
        ...     tamanho_bytes=2048576,
        ...     numero_paginas=45
        ... )
    """

    caminho_arquivo: str
    nome_arquivo: str
    data_carregamento: datetime = field(
        default_factory=datetime.now
    )
    data_ultima_modificacao: Optional[datetime] = None
    status: StatusTexto = StatusTexto.PENDENTE
    secoes: List[Secao] = field(default_factory=list)
    metadados: Optional[MetadadosPDF] = None
    hash_arquivo: Optional[str] = None
    tamanho_bytes: int = 0
    numero_paginas: int = 0
    historico: List[Dict[str, Any]] = field(
        default_factory=list
    )
    info_ia: Dict[str, str] = field(
        default_factory=dict
    )
    _secoes_index: Dict[str, Secao] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        """
        Validações e inicializações pós-criação.

        Raises:
            TextoInvalidoException: Se validações falharem
        """
        self._validar_caminho_arquivo()
        self._reconstruir_index_secoes()

    def _validar_caminho_arquivo(self) -> None:
        """
        Valida caminho do arquivo.

        Raises:
            TextoInvalidoException: Se inválido
        """
        if not self.caminho_arquivo:
            raise TextoInvalidoException(
                "Caminho do arquivo não pode ser vazio"
            )
        caminho = Path(self.caminho_arquivo)
        if not caminho.exists():
            raise TextoInvalidoException(
                f"Arquivo não encontrado: "
                f"{self.caminho_arquivo}"
            )
        if not caminho.is_file():
            raise TextoInvalidoException(
                f"Caminho não é um arquivo: "
                f"{self.caminho_arquivo}"
            )
        
        # Extensões agora são flexíveis (PDF, DOCX, ODT, TEX)
        EXTENSOES_SUPORTADAS = {".pdf", ".docx", ".odt", ".tex", ".md"}
        if caminho.suffix.lower() not in EXTENSOES_SUPORTADAS:
            raise TextoInvalidoException(
                f"Formato não suportado: {caminho.suffix}"
            )

    def _reconstruir_index_secoes(self) -> None:
        """Reconstrói índice de seções para busca rápida."""
        self._secoes_index = {
            s.titulo: s for s in self.secoes
        }

    def calcular_hash(self) -> str:
        """
        Calcula hash SHA-256 do arquivo.

        Lê em chunks de 64KB para suportar arquivos grandes.

        Returns:
            String hexadecimal do hash SHA-256

        Raises:
            TextoInvalidoException: Se houver erro de I/O
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(
                self.caminho_arquivo, "rb"
            ) as f:
                for bloco in iter(
                    lambda: f.read(65536), b""
                ):
                    sha256_hash.update(bloco)
            self.hash_arquivo = sha256_hash.hexdigest()
            self._adicionar_ao_historico(
                "Hash calculado",
                {"hash": self.hash_arquivo},
            )
            return self.hash_arquivo
        except IOError as e:
            raise TextoInvalidoException(
                f"Erro ao calcular hash: {e}"
            )

    def adicionar_secao(self, secao: Secao) -> None:
        """
        Adiciona nova seção ao texto.

        Args:
            secao: Seção a ser adicionada

        Raises:
            SecaoDuplicadaException: Se título duplicado
            ValueError: Se seção for None
        """
        if secao is None:
            raise ValueError(
                "Seção não pode ser None"
            )
        if secao.titulo in self._secoes_index:
            raise SecaoDuplicadaException(
                f"Já existe seção '{secao.titulo}'"
            )
        self.secoes.append(secao)
        self._secoes_index[secao.titulo] = secao
        self._adicionar_ao_historico(
            "Seção adicionada",
            {"titulo": secao.titulo},
        )

    def remover_secao(self, titulo: str) -> None:
        """
        Remove seção pelo título.

        Args:
            titulo: Título da seção

        Raises:
            SecaoNaoEncontradaException: Se não existir
        """
        secao = self.obter_secao_por_titulo(titulo)
        if not secao:
            raise SecaoNaoEncontradaException(
                f"Seção '{titulo}' não encontrada"
            )
        self.secoes.remove(secao)
        del self._secoes_index[titulo]
        self._adicionar_ao_historico(
            "Seção removida", {"titulo": titulo}
        )

    def obter_secao_por_titulo(
        self, titulo: str
    ) -> Optional[Secao]:
        """
        Busca seção pelo título (busca indexada).

        Args:
            titulo: Título exato da seção

        Returns:
            Secao ou None se não encontrada
        """
        return self._secoes_index.get(titulo)

    def obter_secao_por_pagina(
        self, numero_pagina: int
    ) -> Optional[Secao]:
        """
        Busca seção que contém determinada página.

        Args:
            numero_pagina: Número da página (base 1)

        Returns:
            Secao ou None
        """
        for secao in self.secoes:
            inicio = secao.numero_pagina_inicio
            fim = secao.numero_pagina_fim
            if inicio <= numero_pagina <= fim:
                return secao
        return None

    def obter_secoes_por_status(
        self, status: StatusTexto
    ) -> List[Secao]:
        """
        Filtra seções por status.

        Args:
            status: Status a filtrar

        Returns:
            Lista de seções com o status
        """
        return [
            s for s in self.secoes
            if s.status == status
        ]

    def atualizar_status(
        self, novo_status: StatusTexto
    ) -> None:
        """
        Atualiza o status do texto.

        Args:
            novo_status: Novo status
        """
        anterior = self.status
        self.status = novo_status
        self._adicionar_ao_historico(
            "Status atualizado",
            {
                "anterior": anterior.value,
                "novo": novo_status.value,
            },
        )

    def verificar_integridade(self) -> bool:
        """
        Verifica se arquivo corresponde ao hash.

        Returns:
            True se íntegro, False caso contrário

        Raises:
            TextoInvalidoException: Se hash não calculado
        """
        if not self.hash_arquivo:
            raise TextoInvalidoException(
                "Hash do arquivo não foi calculado"
            )
        hash_anterior = self.hash_arquivo
        hash_atual = self.calcular_hash()
        return hash_atual == hash_anterior

    def _adicionar_ao_historico(
        self,
        evento: str,
        detalhes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Adiciona evento ao histórico.

        Args:
            evento: Descrição do evento
            detalhes: Detalhes adicionais
        """
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "evento": evento,
            "detalhes": detalhes or {},
        }
        self.historico.append(entrada)

    @property
    def esta_completo(self) -> bool:
        """Verifica se todas as seções estão concluídas."""
        if not self.secoes:
            return False
        return all(
            s.status == StatusTexto.CONCLUIDO
            for s in self.secoes
        )

    @property
    def progresso_percentual(self) -> float:
        """Percentual de conclusão (0.0 a 100.0)."""
        if not self.secoes:
            return 0.0
        concluidas = len(
            self.obter_secoes_por_status(
                StatusTexto.CONCLUIDO
            )
        )
        return (concluidas / len(self.secoes)) * 100.0

    @property
    def total_erros_encontrados(self) -> int:
        """Total de erros em todas as seções."""
        return sum(
            len(s.obter_todos_erros())
            for s in self.secoes
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário."""
        return {
            "caminho_arquivo": self.caminho_arquivo,
            "nome_arquivo": self.nome_arquivo,
            "data_carregamento": (
                self.data_carregamento.isoformat()
            ),
            "data_ultima_modificacao": (
                self.data_ultima_modificacao.isoformat()
                if self.data_ultima_modificacao
                else None
            ),
            "status": self.status.value,
            "secoes": [
                s.to_dict() for s in self.secoes
            ],
            "metadados": (
                self.metadados.to_dict()
                if self.metadados
                else None
            ),
            "hash_arquivo": self.hash_arquivo,
            "tamanho_bytes": self.tamanho_bytes,
            "numero_paginas": self.numero_paginas,
            "historico": self.historico,
        }

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any]
    ) -> "TextoEstruturado":
        """
        Cria instância a partir de dicionário.

        Args:
            data: Dicionário com dados do texto

        Returns:
            Nova instância de TextoEstruturado
        """
        texto = cls(
            caminho_arquivo=data["caminho_arquivo"],
            nome_arquivo=data["nome_arquivo"],
            status=StatusTexto(
                data.get("status", "pendente")
            ),
            hash_arquivo=data.get("hash_arquivo"),
            tamanho_bytes=data.get("tamanho_bytes", 0),
            numero_paginas=data.get(
                "numero_paginas", 0
            ),
            historico=data.get("historico", []),
        )
        for secao_data in data.get("secoes", []):
            secao = Secao.from_dict(secao_data)
            texto.adicionar_secao(secao)
        return texto

    def __str__(self) -> str:
        """Representação legível."""
        return (
            f"TextoEstruturado({self.nome_arquivo}, "
            f"{len(self.secoes)} seções, "
            f"status={self.status.value})"
        )

    def __repr__(self) -> str:
        """Representação detalhada."""
        h = (
            f"{self.hash_arquivo[:8]}..."
            if self.hash_arquivo
            else "None"
        )
        return (
            f"TextoEstruturado(caminho='{self.caminho_arquivo}', "
            f"secoes={len(self.secoes)}, "
            f"status={self.status.value}, "
            f"hash='{h}')"
        )
