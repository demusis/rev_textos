"""
Gerador de relatórios em formato HTML.

Implementação concreta que gera relatórios de
revisão como páginas HTML estilizadas.
"""

import logging
from datetime import datetime
from pathlib import Path

from ...core.entities.texto_estruturado import TextoEstruturado
from ...core.entities.relatorio import Relatorio
from ...core.enums.formato_relatorio import (
    FormatoRelatorio,
)
from ...core.interfaces.services.i_report_generator import (
    IReportGenerator,
)

logger = logging.getLogger(__name__)

CSS_STYLES = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
        line-height: 1.6; color: #333;
        max-width: 900px; margin: 0 auto;
        padding: 40px 20px; background: #f5f5f5;
    }
    .container {
        background: white; border-radius: 8px;
        padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h1 { color: #1a237e; border-bottom: 3px solid #3f51b5;
        padding-bottom: 10px; margin-bottom: 20px; }
    h2 { color: #283593; margin-top: 30px; margin-bottom: 15px; }
    h3 { color: #3949ab; margin-top: 20px; margin-bottom: 10px; }
    .meta { color: #666; font-size: 0.9em; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse;
        margin: 15px 0; font-size: 0.9em; }
    th { background: #3f51b5; color: white; padding: 12px 8px;
        text-align: left; }
    td { padding: 10px 8px; border-bottom: 1px solid #eee; }
    tr:hover { background: #f5f5ff; }
    .badge { padding: 3px 8px; border-radius: 12px;
        font-size: 0.8em; font-weight: bold; }
    .badge-erro { background: #ffebee; color: #c62828; }
    .badge-ok { background: #e8f5e9; color: #2e7d32; }
    .badge-warn { background: #fff3e0; color: #e65100; }
    .resumo-box { background: #e8eaf6; border-radius: 8px;
        padding: 20px; margin: 20px 0; }
    .severidade { font-size: 1.1em; }
    code { background: #f5f5f5; padding: 2px 6px;
        border-radius: 3px; font-size: 0.9em; }
    .footer { margin-top: 40px; padding-top: 20px;
        border-top: 1px solid #ddd; color: #999;
        font-size: 0.8em; text-align: center; }
    ul, ol { margin-left: 20px; margin-bottom: 10px; }
    li { margin-bottom: 5px; }
</style>
"""


class HtmlReportGenerator(IReportGenerator):
    """
    Gerador de relatórios em HTML.

    Produz relatórios estilizados com CSS
    para visualização no navegador.
    """

    def gerar(self, texto: TextoEstruturado) -> Relatorio:
        """Gera relatório HTML a partir do texto."""
        partes = []

        partes.append("<!DOCTYPE html>")
        partes.append(
            '<html lang="pt-BR"><head>'
        )
        partes.append(
            '<meta charset="UTF-8">'
        )
        partes.append(
            '<meta name="viewport" content='
            '"width=device-width, initial-scale=1.0">'
        )
        partes.append(
            f"<title>Revisão — "
            f"{texto.nome_arquivo}</title>"
        )
        partes.append(CSS_STYLES)
        partes.append("</head><body>")
        partes.append('<div class="container">')

        # Cabeçalho
        partes.append(
            f"<h1>📋 Relatório de Revisão</h1>"
        )
        partes.append(
            f'<div class="meta">'
            f"<strong>{texto.nome_arquivo}</strong>"
            f" — {datetime.now():%d/%m/%Y %H:%M}"
        )

        # Seção de Informações da IA (Detalhada)
        info_ia = texto.info_ia
        perfis = info_ia.get("perfis", {})
        fases = info_ia.get("fases", {})

        if perfis and isinstance(perfis, dict):
             # Estilo inline para a caixa de detalhes da IA
            partes.append(
                "<div style='margin-top: 15px; padding: 12px; background: #f8f9fa; "
                "border-radius: 6px; border: 1px solid #e9ecef; font-size: 0.9em;'>"
            )
            
            # 1. Lista de Modelos (Perfis)
            partes.append(
                "<div style='margin-bottom: 8px;'>"
                "<strong style='color: #2c3e50;'>🧠 Modelos por Complexidade:</strong>"
                "<ul style='margin: 5px 0 0 20px; color: #444;'>"
            )
            for nome_perfil, dados in perfis.items():
                prov = dados.get('provider', '?').capitalize()
                mod = dados.get('model', '?')
                nome_p = nome_perfil.capitalize()
                partes.append(
                    f"<li><strong>{nome_p}:</strong> {prov} "
                    f"<span style='color: #777;'>({mod})</span></li>"
                )
            partes.append("</ul></div>")

            # 2. Mapeamento de Fases
            if fases:
                partes.append(
                    "<div>"
                    "<strong style='color: #2c3e50;'>⚙️ Complexidade por Fase:</strong>"
                    "<div style='margin-top: 5px; display: flex; flex-wrap: wrap; gap: 8px;'>"
                )
                
                # Mapa de labels amigáveis
                labels_fase = {
                    "gramatical": "Gramatical",
                    "tecnica": "Técnica",
                    "estrutural": "Estrutural",
                    "validacao": "Validação",
                    "consistencia": "Consistência",
                    "sintese": "Síntese"
                }

                for fase_key, perfil_key in fases.items():
                    label = labels_fase.get(fase_key, fase_key.capitalize())
                    perfil_fmt = perfil_key.capitalize()
                    partes.append(
                        f"<span style='background: white; border: 1px solid #ced4da; "
                        f"padding: 2px 8px; border-radius: 12px; font-size: 0.85em; color: #495057;'>"
                        f"<b>{label}:</b> {perfil_fmt}</span>"
                    )
                partes.append("</div></div>")
            
            partes.append("</div>") # Fecha container IA

        elif texto.info_ia:
            # Fallback para formato antigo
            partes.append(
                f" — IA: {texto.info_ia.get('provedor')} "
                f"({texto.info_ia.get('modelo')})"
            )
        partes.append("</div>")

        # Resumo
        total_erros = texto.total_erros_encontrados
        badge = (
            "badge-ok"
            if total_erros == 0
            else "badge-warn"
            if total_erros < 10
            else "badge-erro"
        )
        partes.append(
            f'<div class="resumo-box">'
            f"<h2>Resumo</h2>"
            f"<table>"
            f"<tr><td>Seções analisadas</td>"
            f"<td><strong>{len(texto.secoes)}"
            f"</strong></td></tr>"
            f"<tr><td>Total de erros</td>"
            f'<td><span class="badge {badge}">'
            f"{total_erros}</span></td></tr>"
            f"<tr><td>Status</td>"
            f"<td>{texto.status.value}</td></tr>"
            f"<tr><td>Tempo Processamento</td>"
            f"<td>{str(datetime.now() - texto.data_carregamento).split('.')[0]}</td></tr>"
            f"<tr><td>Progresso</td>"
            f"<td>{texto.progresso_percentual:.0f}%"
            f"</td></tr>"
            f"</table></div>"
        )

        # Análise de Consistência
        if texto.analise_consistencia:
            partes.append(
                f'<div class="resumo-box">'
                f"<h2>Análise de Consistência</h2>"
                f"<div style='background: white; padding: 15px; border-radius: 4px; border-left: 4px solid #3f51b5;'>"
                f"{self._render_consistencia_tabela(texto.analise_consistencia)}"
                f"</div></div>"
            )

        # Síntese Geral
        if texto.sintese_geral:
            partes.append(
                f'<div class="resumo-box">'
                f"<h2>Síntese Geral</h2>"
                f"<div style='background: white; padding: 15px; border-radius: 4px; border-left: 4px solid #2e7d32;'>"
                f"{self._markdown_to_html(texto.sintese_geral)}"
                f"</div></div>"
            )

        # Seções
        partes.append("<h2>Detalhes por Seção</h2>")
        for secao in texto.secoes:
            partes.append(
                f"<h3>{secao.titulo}</h3>"
            )
            partes.append(
                f"<p>Páginas "
                f"{secao.numero_pagina_inicio}"
                f"–{secao.numero_pagina_fim} | "
                f"Status: {secao.status.value} | "
                f"{secao.total_iteracoes} "
                f"iterações</p>"
            )

            erros = secao.obter_todos_erros()
            if erros:
                partes.append(
                    "<table><tr>"
                    "<th>#</th><th>Tipo</th>"
                    "<th>Original</th>"
                    "<th>Justificativa</th>"
                    "<th>Correção</th></tr>"
                )
                for i, erro in enumerate(erros, 1):
                    sev = "⚠️" * erro.severidade
                    partes.append(
                        f"<tr><td>{i}</td>"
                        f"<td>{erro.tipo.value}</td>"
                        f"<td><code>"
                        f"{erro.trecho_original}"
                        f"</code></td>"
                        f"<td>"
                        f"{erro.descricao}"
                        f"</td>"
                        f"<td><code>"
                        f"{erro.sugestao_correcao}"
                        f"</code></td></tr>"
                    )
                partes.append("</table>")
            else:
                partes.append(
                    "<p><em>Nenhum erro.</em></p>"
                )

        # Rodapé
        partes.append(
            '<div class="footer">'
            "Gerado pelo Sistema de Revisão "
            "de Textos Estruturados</div>"
        )

        partes.append("</div></body></html>")
        conteudo = "\n".join(partes)

        return Relatorio(
            titulo=(
                f"Revisão — {texto.nome_arquivo}"
            ),
            formato=FormatoRelatorio.HTML,
            conteudo=conteudo,
            texto_nome=texto.nome_arquivo,
            total_secoes=len(texto.secoes),
            total_erros=total_erros,
        )

    def obter_formato(self) -> FormatoRelatorio:
        return FormatoRelatorio.HTML

    def _markdown_to_html(self, text: str) -> str:
        """Converte markdown básico para HTML (bold, italic, lists)."""
        if not text:
            return ""
        
        import re
        
        # 1. Escapar HTML para segurança
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # 2. Bold: **text**
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text, flags=re.DOTALL)
        
        # 3. Italic: *text* (evitando casar o que já é bold)
        text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text, flags=re.DOTALL)
        
        # 4. Processar linhas para listas
        lines = text.split('\n')
        new_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            # Detectar marcadores de lista (- ou *)
            # Regex: início da linha opcionalmente com espaços, seguido de - ou *, seguido de espaço
            match = re.match(r'^[\s]*[\-\*][\s]+(.*)', line)
            
            if match:
                if not in_list:
                    new_lines.append('<ul>')
                    in_list = True
                content = match.group(1)
                new_lines.append(f'<li>{content}</li>')
            else:
                if in_list:
                    new_lines.append('</ul>')
                    in_list = False
                new_lines.append(line)
        
        if in_list:
            new_lines.append('</ul>')
            
        # 5. Juntar e converter quebras de linha em <br> (exceto em listas)
        final_text = ""
        for i, line in enumerate(new_lines):
            final_text += line
            # Adicionar <br> se não for tag de lista ou se a próxima linha não for fechamento/abertura de lista
            if not line.endswith('<ul>') and not line.endswith('</ul>') and not line.startswith('<li>'):
                if i < len(new_lines) - 1 and not new_lines[i+1].startswith('<li>') and not new_lines[i+1].startswith('</ul>'):
                    final_text += "<br>"
        
        return final_text

    def _render_consistencia_tabela(self, content: str) -> str:
        """Tenta parsear JSON de consistência e renderiza como tabela HTML."""
        if not content:
            return ""
            
        try:
            import json
            dados = json.loads(content)
            inconsistencias = dados.get("inconsistencias", [])
            
            if not inconsistencias:
                resumo = dados.get("resumo")
                if resumo:
                    return f"<p>{resumo}</p>"
                return self._markdown_to_html(content)
                
            # Construir tabela HTML
            html = [
                "<table>",
                "<thead><tr>",
                "<th>Seção 1</th>",
                "<th>Seção 2</th>",
                "<th>Descrição</th>",
                "<th style='width: 80px;'>Sev</th>",
                "<th>Sugestão</th>",
                "</tr></thead>",
                "<tbody>"
            ]
            
            for inc in inconsistencias:
                s1 = inc.get("secao_1", "-")
                s2 = inc.get("secao_2", "-")
                desc = inc.get("descricao", "")
                sev_num = inc.get("severidade", 1)
                sev = "⚠️" * sev_num
                sug = inc.get("sugestao", "")
                
                html.append("<tr>")
                html.append(f"<td>{s1}</td>")
                html.append(f"<td>{s2}</td>")
                html.append(f"<td>{desc}</td>")
                html.append(f"<td>{sev}</td>")
                html.append(f"<td>{sug}</td>")
                html.append("</tr>")
                
            html.append("</tbody></table>")
            
            # Adicionar resumo se existir
            resumo = dados.get("resumo")
            if resumo:
                html.append(f"<p style='margin-top: 15px;'><strong>Resumo:</strong> {resumo}</p>")
                
            return "\n".join(html)
            
        except Exception:
            # Fallback para markdown tradicional
            return self._markdown_to_html(content)

    def salvar(
        self,
        relatorio: Relatorio,
        caminho: str,
    ) -> str:
        """Salva relatório como arquivo .html."""
        dir_path = Path(caminho)
        dir_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        nome_base = Path(relatorio.texto_nome).stem
        nome_arquivo = (
            f"revisao_{nome_base}_{timestamp}.html"
        )
        caminho_completo = dir_path / nome_arquivo

        caminho_completo.write_text(
            relatorio.conteudo, encoding="utf-8"
        )
        relatorio.caminho_arquivo = str(
            caminho_completo
        )

        logger.info(
            f"Relatório HTML salvo: "
            f"{caminho_completo}"
        )
        return str(caminho_completo)
