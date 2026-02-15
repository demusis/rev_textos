"""
Validador de configurações do sistema.

Contém regras de validação para configurações
do aplicativo e prompts de IA.
"""

from typing import List, Tuple, Dict, Any

# Chaves obrigatórias na configuração principal
CHAVES_OBRIGATORIAS = [
    "gemini_model",
    "max_retries",
    "timeout",
]

# Modelos Gemini suportados
MODELOS_SUPORTADOS = [
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-pro-preview-05-06",
]


class ConfigValidator:
    """
    Validador de configurações do sistema.

    Verifica se as configurações possuem todos os
    campos obrigatórios e valores válidos.

    Example:
        >>> validator = ConfigValidator()
        >>> valido, erros = validator.validar(config)
    """

    def validar(
        self, config: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Executa validação completa das configurações.

        Args:
            config: Dicionário de configurações

        Returns:
            Tupla (é_válido, lista_de_erros)
        """
        erros: List[str] = []

        erros.extend(
            self._validar_chaves_obrigatorias(config)
        )
        erros.extend(
            self._validar_modelo(config)
        )
        erros.extend(
            self._validar_parametros_numericos(config)
        )

        return len(erros) == 0, erros

    def _validar_chaves_obrigatorias(
        self, config: Dict[str, Any]
    ) -> List[str]:
        """Verifica presença de chaves obrigatórias."""
        erros: List[str] = []

        for chave in CHAVES_OBRIGATORIAS:
            if chave not in config:
                erros.append(
                    f"Configuração obrigatória "
                    f"ausente: '{chave}'"
                )

        return erros

    def _validar_modelo(
        self, config: Dict[str, Any]
    ) -> List[str]:
        """Valida modelo de IA configurado."""
        erros: List[str] = []
        modelo = config.get("gemini_model", "")

        if modelo and modelo not in MODELOS_SUPORTADOS:
            erros.append(
                f"Modelo não suportado: '{modelo}'. "
                f"Suportados: {MODELOS_SUPORTADOS}"
            )

        return erros

    def _validar_parametros_numericos(
        self, config: Dict[str, Any]
    ) -> List[str]:
        """Valida parâmetros numéricos."""
        erros: List[str] = []

        retries = config.get("max_retries", 3)
        if not 1 <= retries <= 10:
            erros.append(
                f"max_retries deve ser 1-10: {retries}"
            )

        timeout = config.get("timeout", 120)
        if not 30 <= timeout <= 300:
            erros.append(
                f"timeout deve ser 30-300: {timeout}"
            )

        return erros
