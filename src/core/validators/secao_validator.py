"""
Validador da entidade Seção.

Contém regras de validação de negócio para seções
de textos estruturados.
"""

from typing import List, Tuple

from ..entities.secao import Secao

# Tamanho mínimo de conteúdo para revisão (caracteres)
MIN_CONTEUDO_CHARS = 10
# Tamanho máximo de conteúdo por seção (caracteres)
MAX_CONTEUDO_CHARS = 500_000


class SecaoValidator:
    """
    Validador de regras de negócio para seções.

    Aplica validações de conteúdo e estrutura
    além das validações básicas da entidade.

    Example:
        >>> validator = SecaoValidator()
        >>> valido, erros = validator.validar(secao)
    """

    def validar(
        self, secao: Secao
    ) -> Tuple[bool, List[str]]:
        """
        Executa todas as validações na seção.

        Args:
            secao: Seção a ser validada

        Returns:
            Tupla (é_válido, lista_de_erros)
        """
        erros: List[str] = []

        erros.extend(self._validar_conteudo(secao))
        erros.extend(self._validar_titulo(secao))
        erros.extend(self._validar_paginacao(secao))

        return len(erros) == 0, erros

    def _validar_conteudo(
        self, secao: Secao
    ) -> List[str]:
        """Valida conteúdo da seção."""
        erros: List[str] = []

        if secao.tamanho_conteudo < MIN_CONTEUDO_CHARS:
            erros.append(
                f"Conteúdo muito curto: "
                f"{secao.tamanho_conteudo} caracteres "
                f"(mínimo: {MIN_CONTEUDO_CHARS})"
            )
        elif secao.tamanho_conteudo > MAX_CONTEUDO_CHARS:
            erros.append(
                f"Conteúdo muito longo: "
                f"{secao.tamanho_conteudo} caracteres "
                f"(máximo: {MAX_CONTEUDO_CHARS})"
            )

        return erros

    def _validar_titulo(
        self, secao: Secao
    ) -> List[str]:
        """Valida título da seção."""
        erros: List[str] = []

        if len(secao.titulo) > 200:
            erros.append(
                "Título muito longo (máximo: 200 chars)"
            )

        return erros

    def _validar_paginacao(
        self, secao: Secao
    ) -> List[str]:
        """Valida paginação da seção."""
        erros: List[str] = []

        if secao.numero_paginas > 100:
            erros.append(
                f"Seção muito extensa: "
                f"{secao.numero_paginas} páginas"
            )

        return erros
