# Revisor de Textos Estruturados (RTE)

Sistema especializado para a revisão técnica e linguística de documentos estruturados (laudos periciais, artigos científicos, contratos) fundamentado em modelos de linguagem de grande escala (LLMs).

O sistema submete o documento a múltiplos ciclos de análise iterativa, permitindo a identificação e correção de inconsistências gramaticais, estruturais, técnicas e lógicas, garantindo a integridade e o rigor acadêmico do texto final.

## Funcionalidades Principais

### Integração com Múltiplos Provedores de IA
O RTE suporta diversos motores de inferência para otimização do processo de revisão:
-   **Google Gemini**: Alta eficiência em processamento de longos contextos (ex: `gemini-2.0-flash`).
-   **Groq**: Desempenho superior em latência para revisões expeditas.
-   **OpenRouter**: Acesso unificado a modelos de ponta (GPT-4, Claude 3, Mistral).
-   **Modo Simulação (Mock)**: Ambiente controlado para validação de interface e fluxos.

### Metodologia de Revisão Iterativa
Diferente de sistemas de correção convencionais, o RTE emprega um algoritmo de refinamento progressivo:
1.  **Análise Primária**: Identificação inicial de desvios normativos.
2.  **Refinamento Progressivo**: O texto resultante de cada ciclo serve de entrada para o subsequente.
3.  **Convergência Terapêutica**: O processo encerra-se após a estabilização do texto (ausência de novos erros) ou ao atingir o limite configurado de iterações.

### Relatórios Analíticos Consolidados
Geração de diagnósticos detalhados em formatos **HTML** e **Markdown**, incluindo:
-   **Histórico de Revisão**: Registro exaustivo de todas as supressões e correções realizadas.
-   **Análise de Consistência**: Tabela comparativa identificando contradições internas e divergências factuais entre seções do documento.
-   **Métricas de Desempenho**: Quantificação de erros por categoria, consumo de recursos e tempo de processamento.

### Interface de Gestão (GUI)
Console administrativo desenvolvido em PyQt6 para controle granular do processo:
-   **Parametrização Dinâmica**: Ajuste de temperatura, tokens e limiares de convergência.
-   **Gestão de Prompts**: Customização de diretrizes de revisão técnica e estrutural.
-   **Persistência de Configurações**: Exportação e importação de perfis de análise.

---

## Arquitetura

Clean Architecture em 4 camadas para robustez e manutenção:

```
src/
├── core/           # Regras de Negócio (Entidades, Interfaces)
├── application/    # Casos de Uso (Orquestração da Revisão)
├── infrastructure/ # Implementações (Gateways de IA, PDF, Relatórios)
└── presentation/   # Interface Gráfica (Windows/Linux/macOS)
```

## Pré-requisitos

-   Python 3.10 ou superior.
-   Chave de API de pelo menos um provedor:
    -   [Google AI Studio](https://aistudio.google.com/)
    -   [Groq Cloud](https://console.groq.com/)
    -   [OpenRouter](https://openrouter.ai/)

## Instalação

1.  **Clonar o repositório**
    ```bash
    git clone https://github.com/demusis/rev_textos.git
    cd rev_textos
    ```

2.  **Instalar dependências**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuração (Opcional via .env)**
    Você pode configurar via interface gráfica ou criar um arquivo `.env`:
    ```bash
    cp .env.example .env
    ```
    Exemplo de `.env`:
    ```ini
    GEMINI_API_KEY=sua_chave_aqui
    GROQ_API_KEY=sua_chave_aqui
    OPENROUTER_API_KEY=sua_chave_aqui
    ```

## Como Usar

Execute o arquivo principal para abrir a interface:

```bash
python main.py
```

### Passo a Passo

1.  **Carregar Arquivo**: Arraste um PDF ou arquivo de texto para a área de upload.
2.  **Configurações** (⚙️):
    -   Vá na aba **IA / Provedores**.
    -   Selecione o provedor (Gemini, Groq ou OpenRouter).
    -   Cole sua API Key (se não estiver no .env).
    -   O sistema buscará automaticamente os modelos disponíveis. Selecione um.
3.  **Parâmetros**:
    -   Ajuste **Iterações Máx.** (recomendado: 3 a 5).
    -   Defina **Limiar de Convergência** (padrão: 0.95).
4.  **Executar**:
    -   Clique em **Iniciar Revisão**.
    -   Acompanhe o progresso em tempo real na barra lateral.
5.  **Resultados**:
    -   Ao finalizar, o relatório HTML abrirá automaticamente.
    -   Arquivos ficam salvos na pasta `output/`.

