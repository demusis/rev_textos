"""
Repositório de textos estruturados em JSON.

Implementação concreta que persiste textos como
arquivos JSON no sistema de arquivos local.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from ...core.entities.texto_estruturado import TextoEstruturado
from ...core.interfaces.repositories.i_texto_repository import (
    ITextoRepository,
)

logger = logging.getLogger(__name__)


class JsonTextoRepository(ITextoRepository):
    """
    Repositório de textos usando arquivos JSON.

    Persiste os textos processados como arquivos JSON
    em um diretório configurável.

    Attributes:
        _diretorio: Caminho do diretório de dados
    """

    def __init__(
        self, diretorio: str = "./data/textos"
    ) -> None:
        """
        Inicializa o repositório.

        Args:
            diretorio: Diretório para armazenar JSONs
        """
        self._diretorio = Path(diretorio)
        self._diretorio.mkdir(
            parents=True, exist_ok=True
        )

    def salvar(self, texto: TextoEstruturado) -> None:
        """Salva texto como arquivo JSON."""
        if not texto.hash_arquivo:
            texto.calcular_hash()

        caminho = (
            self._diretorio
            / f"{texto.hash_arquivo[:16]}.json"
        )

        dados = texto.to_dict()
        caminho.write_text(
            json.dumps(
                dados,
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        logger.info(
            f"Texto salvo: {caminho.name}"
        )

    def buscar_por_hash(
        self, hash_arquivo: str
    ) -> Optional[TextoEstruturado]:
        """Busca texto pelo hash do arquivo."""
        caminho = (
            self._diretorio
            / f"{hash_arquivo[:16]}.json"
        )

        if not caminho.exists():
            return None

        try:
            dados = json.loads(
                caminho.read_text(encoding="utf-8")
            )
            return TextoEstruturado.from_dict(dados)
        except Exception as e:
            logger.error(
                f"Erro ao carregar texto: {e}"
            )
            return None

    def listar_todos(self) -> List[TextoEstruturado]:
        """Lista todos os textos salvos."""
        textos: List[TextoEstruturado] = []

        for arquivo in self._diretorio.glob(
            "*.json"
        ):
            try:
                dados = json.loads(
                    arquivo.read_text(
                        encoding="utf-8"
                    )
                )
                textos.append(
                    TextoEstruturado.from_dict(dados)
                )
            except Exception as e:
                logger.warning(
                    f"Ignorando {arquivo}: {e}"
                )

        return textos

    def remover(self, hash_arquivo: str) -> None:
        """Remove texto pelo hash."""
        caminho = (
            self._diretorio
            / f"{hash_arquivo[:16]}.json"
        )

        if caminho.exists():
            caminho.unlink()
            logger.info(
                f"Texto removido: {caminho.name}"
            )
