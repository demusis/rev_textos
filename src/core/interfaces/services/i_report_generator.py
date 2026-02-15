"""
Interface para geração de relatórios.

Define o contrato para geradores de relatório em diferentes
formatos (Markdown, HTML, PDF, etc).
"""

from abc import ABC, abstractmethod
from ...entities.texto_estruturado import TextoEstruturado
from ...entities.relatorio import Relatorio
from ...enums.formato_relatorio import FormatoRelatorio


class IReportGenerator(ABC):
    """
    Interface para geradores de relatório.

    Encapsula a lógica de formatação dos resultados
    da revisão em um arquivo de saída.
    """

    @abstractmethod
    def gerar(self, texto: TextoEstruturado) -> Relatorio:
        """
        Gera uma instância de Relatorio a partir do texto.

        Args:
            texto: Texto processado com revisões

        Returns:
            Entidade Relatorio com o conteúdo formatado
        """
        pass

    @abstractmethod
    def salvar(self, relatorio: Relatorio, diretorio: str) -> str:
        """
        Salva o relatório em um arquivo no diretório especificado.

        Args:
            relatorio: Entidade Relatorio a ser salva
            diretorio: Caminho do diretório de saída

        Returns:
            Caminho completo do arquivo gerado
        """
        pass

    @abstractmethod
    def obter_formato(self) -> FormatoRelatorio:
        """Retorna o formato suportado por este gerador."""
        pass
