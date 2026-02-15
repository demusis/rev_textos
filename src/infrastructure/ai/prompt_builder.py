"""
Construtor de prompts para os agentes de IA.

Gerencia templates de prompts estruturados para
cada tipo de agente e caso de uso.
"""

from typing import Dict, Any, Optional


# Templates de prompt em PT-BR
PROMPTS: Dict[str, str] = {
    "revisao_gramatical": """
Você é um revisor linguístico especialista em português brasileiro.
Analise o seguinte trecho de um texto estruturado e identifique TODOS
os erros gramaticais, ortográficos e de concordância.

Para cada erro encontrado, forneça:
1. Trecho original com erro
2. Correção sugerida
3. Tipo do erro (gramatical, ortografico, concordancia)
4. Justificativa técnica

Texto para revisão:
{texto}

Responda em formato JSON com a seguinte estrutura:
{{
  "erros": [
    {{
      "trecho_original": "...",
      "sugestao_correcao": "...",
      "tipo": "gramatical|ortografico|concordancia",
      "justificativa": "...",
      "severidade": 1-5
    }}
  ],
  "texto_revisado": "texto completo com correções aplicadas"
}}
""".strip(),
    "revisao_tecnica": """
Você é um perito criminal com vasta experiência em textos estruturados.
Analise o seguinte trecho de um texto estruturado e identifique
problemas técnicos, incluindo:

- Inconsistências lógicas ou factuais
- Terminologia técnica incorreta ou imprecisa
- Falta de fundamentação científica
- Conclusões não suportadas pelas evidências
- Referências normativas incorretas

Texto para revisão:
{texto}

Responda em formato JSON:
{{
  "erros": [
    {{
      "trecho_original": "...",
      "sugestao_correcao": "...",
      "tipo": "tecnico|inconsistencia|terminologia|fundamentacao",
      "justificativa": "...",
      "severidade": 1-5
    }}
  ],
  "texto_revisado": "texto completo com correções"
}}
""".strip(),
    "revisao_estrutural": """
Você é um especialista em redação técnica e textos estruturados.
Analise a estrutura do seguinte trecho, verificando:

- Coesão e coerência textual
- Organização lógica dos argumentos
- Clareza e objetividade da redação
- Formatação adequada para texto estruturado
- Completude das informações necessárias

Texto para revisão:
{texto}

Responda em formato JSON:
{{
  "erros": [
    {{
      "trecho_original": "...",
      "sugestao_correcao": "...",
      "tipo": "estrutural|coesao|clareza|formatacao",
      "justificativa": "...",
      "severidade": 1-5
    }}
  ],
  "texto_revisado": "texto completo com correções"
}}
""".strip(),
    "validacao": """
Você é um revisor sênior de textos estruturados.
Compare o texto original com a versão revisada e avalie
se as correções propostas são adequadas.

Texto original:
{texto_original}

Texto revisado:
{texto_revisado}

Correções aplicadas:
{correcoes}

Para cada correção, indique se está:
- CORRETA: a correção melhora o texto
- INCORRETA: a correção introduz erro
- DESNECESSARIA: o texto original estava correto

Responda em formato JSON:
{{
  "avaliacoes": [
    {{
      "correcao": "...",
      "status": "correta|incorreta|desnecessaria",
      "justificativa": "..."
    }}
  ],
  "aprovado": true/false
}}
""".strip(),
    "consistencia": """
Você é um especialista em análise de consistência documental.
Analise as seguintes seções de um texto estruturado e identifique
inconsistências entre elas.

Verifique:
- Contradições entre seções
- Dados divergentes (datas, nomes, valores)
- Referências cruzadas incorretas
- Conclusões incompatíveis com a metodologia

Seções do texto:
{secoes}

Responda em formato JSON:
{{
  "inconsistencias": [
    {{
      "secao_1": "título da seção",
      "secao_2": "título da seção",
      "descricao": "...",
      "severidade": 1-5,
      "sugestao": "..."
    }}
  ],
  "consistente": true/false,
  "resumo": "resumo da análise"
}}
""".strip(),
    "sintese": """
Você é um redator técnico especializado em textos estruturados.
Gere um resumo executivo das revisões realizadas no texto.

Inclua:
- Total de erros por categoria
- Seções com mais problemas
- Avaliação geral da qualidade
- Recomendações prioritárias

Dados do processamento:
{dados}

Responda em texto corrido em português brasileiro,
com parágrafos claros e objetivos.
""".strip(),
}


class PromptBuilder:
    """
    Construtor de prompts para agentes de IA.

    Gerencia templates e substitui variáveis
    para gerar prompts completos.

    Example:
        >>> builder = PromptBuilder()
        >>> prompt = builder.construir(
        ...     "revisao_gramatical",
        ...     texto="Conteúdo para revisão..."
        ... )
    """

    def __init__(
        self,
        templates_customizados: Optional[
            Dict[str, str]
        ] = None,
    ) -> None:
        """
        Inicializa o construtor.

        Args:
            templates_customizados: Templates extras
        """
        self._templates = dict(PROMPTS)
        if templates_customizados:
            self._templates.update(
                templates_customizados
            )

    def construir(
        self,
        tipo: str,
        **kwargs: Any,
    ) -> str:
        """
        Constrói prompt a partir do template.

        Args:
            tipo: Tipo do prompt (chave do template)
            **kwargs: Variáveis para substituição

        Returns:
            Prompt completo

        Raises:
            ValueError: Se tipo não existir
        """
        template = self._templates.get(tipo)
        if not template:
            tipos = list(self._templates.keys())
            raise ValueError(
                f"Tipo de prompt '{tipo}' não encontrado."
                f" Disponíveis: {tipos}"
            )

        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(
                f"Variável {e} não fornecida "
                f"para template '{tipo}'"
            )

    def listar_tipos(self) -> list:
        """Lista tipos de prompt disponíveis."""
        return list(self._templates.keys())

    def adicionar_template(
        self, tipo: str, template: str
    ) -> None:
        """
        Adiciona ou sobrescreve template.

        Args:
            tipo: Identificador do template
            template: Conteúdo do template
        """
        self._templates[tipo] = template
