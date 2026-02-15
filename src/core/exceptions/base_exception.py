"""
Módulo de exceção base do sistema.

Define a classe base para todas as exceções customizadas
do sistema de revisão de textos.
"""


class RevisorTextosException(Exception):
    """
    Exceção base para todo o sistema Revisor de Textos.

    Todas as exceções customizadas do sistema devem herdar
    desta classe para permitir captura genérica e tratamento
    uniforme de erros.

    Attributes:
        mensagem: Descrição do erro ocorrido
        codigo: Código identificador do erro (opcional)
        detalhes: Informações adicionais sobre o erro

    Example:
        >>> raise RevisorTextosException(
        ...     "Erro ao processar texto",
        ...     codigo="ERR_001"
        ... )
    """

    def __init__(
        self,
        mensagem: str,
        codigo: str = "",
        detalhes: str = "",
    ) -> None:
        """
        Inicializa a exceção base.

        Args:
            mensagem: Descrição do erro
            codigo: Código identificador do erro
            detalhes: Informações adicionais
        """
        self.mensagem = mensagem
        self.codigo = codigo
        self.detalhes = detalhes
        super().__init__(self.mensagem)

    def __str__(self) -> str:
        """Retorna representação legível da exceção para o usuário."""
        # Prioriza a mensagem amigável formatada
        return self.mensagem
