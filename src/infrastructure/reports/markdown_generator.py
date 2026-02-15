"""
Gerador de relatórios em formato Markdown.

Implementação concreta que gera relatórios de
revisão em Markdown formatado.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from ...core.entities.texto_estruturado import TextoEstruturado
from ...core.entities.relatorio import Relatorio
from ...core.enums.formato_relatorio import (
    FormatoRelatorio,
)
from ...core.interfaces.services.i_report_generator import (
    IReportGenerator,
)

logger = logging.getLogger(__name__)


class MarkdownReportGenerator(IReportGenerator):
    """
    Gerador de relatórios em Markdown.

    Produz relatórios de revisão formatados em
    Markdown com sumário, erros e métricas.
    """

    def gerar(self, texto: TextoEstruturado) -> Relatorio:
        """Gera relatório Markdown a partir do texto."""
        secoes_md = []

        # Cabeçalho
        secoes_md.append(
            f"# Relatório de Revisão — "
            f"{texto.nome_arquivo}\n"
        )
        secoes_md.append(
            f"**Data**: "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
            f"\n"
        )
        if texto.info_ia:
            secoes_md.append(
                f"**IA**: {texto.info_ia.get('provedor')} "
                f"({texto.info_ia.get('modelo')})\n"
            )

        # Resumo
        secoes_md.append("## Resumo\n")
        secoes_md.append(
            f"| Métrica | Valor |\n"
            f"|---------|-------|\n"
            f"| Seções analisadas | "
            f"{len(texto.secoes)} |\n"
            f"| Total de erros | "
            f"{texto.total_erros_encontrados} |\n"
            f"| Status | {texto.status.value} |\n"
            f"| Progresso | "
            f"{texto.progresso_percentual:.0f}% |\n"
        )

        # Detalhes por seção
        secoes_md.append(
            "## Detalhes por Seção\n"
        )
        for secao in texto.secoes:
            secoes_md.append(
                f"### {secao.titulo}\n"
            )
            secoes_md.append(
                f"- **Páginas**: "
                f"{secao.numero_pagina_inicio}"
                f"–{secao.numero_pagina_fim}\n"
                f"- **Status**: "
                f"{secao.status.value}\n"
                f"- **Iterações**: "
                f"{secao.total_iteracoes}\n"
            )

            erros = secao.obter_todos_erros()
            if erros:
                secoes_md.append(
                    "#### Erros Encontrados\n"
                )
                secoes_md.append(
                    "| # | Tipo | Severidade "
                    "| Original | Justificativa | Correção |\n"
                    "|---|------|------------|"
                    "----------|---------------|----------|\n"
                )
                for i, erro in enumerate(erros, 1):
                    orig = erro.trecho_original
                    corr = erro.sugestao_correcao
                    just = erro.descricao
                    secoes_md.append(
                        f"| {i} | "
                        f"{erro.tipo.value} | "
                        f"{'⚠️' * erro.severidade} | "
                        f"`{orig}` | "
                        f"{just} | "
                        f"`{corr}` |\n"
                    )
            else:
                secoes_md.append(
                    "*Nenhum erro encontrado.*\n"
                )

            secoes_md.append("")

        # Rodapé
        secoes_md.append("---\n")
        secoes_md.append(
            "*Relatório gerado automaticamente pelo "
            "Sistema de Revisão de Textos Estruturados.*\n"
        )

        conteudo = "\n".join(secoes_md)

        return Relatorio(
            titulo=(
                f"Revisão — {texto.nome_arquivo}"
            ),
            formato=FormatoRelatorio.MARKDOWN,
            conteudo=conteudo,
            texto_nome=texto.nome_arquivo,
            total_secoes=len(texto.secoes),
            total_erros=(
                texto.total_erros_encontrados
            ),
        )

    def obter_formato(self) -> FormatoRelatorio:
        return FormatoRelatorio.MARKDOWN

    def salvar(
        self,
        relatorio: Relatorio,
        caminho: str,
    ) -> str:
        """Salva relatório como arquivo .md."""
        dir_path = Path(caminho)
        dir_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        nome_base = Path(relatorio.texto_nome).stem
        nome_arquivo = (
            f"revisao_{nome_base}_{timestamp}.md"
        )
        caminho_completo = dir_path / nome_arquivo

        caminho_completo.write_text(
            relatorio.conteudo, encoding="utf-8"
        )
        relatorio.caminho_arquivo = str(
            caminho_completo
        )

        logger.info(
            f"Relatório salvo: {caminho_completo}"
        )
        return str(caminho_completo)
