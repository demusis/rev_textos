"""
Módulo de validação de textos estruturados.

Define regras de negócio e integridade para a entidade
TextoEstruturado.
"""

from typing import List, Tuple

from ..entities.texto_estruturado import TextoEstruturado


class TextoValidator:
    """
    Validador de regras de negócio para textos estruturados.

    Verifica se o texto carregado atende aos requisitos
    mínimos para processamento.
    """

    def validar(
        self, texto: TextoEstruturado
    ) -> Tuple[bool, List[str]]:
        """
        Executa todas as validações no texto.

        Args:
            texto: Texto a ser validado

        Returns:
            Tupla (sucesso, lista de erros)
        """
        erros = []

        # 1. Verificar se há conteúdo
        if not texto.nome_arquivo:
            erros.append("Nome do arquivo não definido")

        # 2. Verificar se o hash foi calculado
        if not texto.hash_arquivo:
            erros.append(
                "Integridade não verificada (hash ausente)"
            )

        # 3. Validar se é PDF ou formato suportado (já feito na entidade, mas podemos reforçar)
        if texto.tamanho_bytes <= 0:
            erros.append("Arquivo vazio (0 bytes)")

        return len(erros) == 0, erros
