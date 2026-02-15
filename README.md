# 📋 Revisor de Textos Estruturados

Sistema avançado de revisão automática de textos estruturados (laudos, artigos, contratos) utilizando Inteligência Artificial.

O sistema processa documentos (PDF, Markdown), identifica seções e aplica múltiplos ciclos de revisão iterativa para garantir qualidade gramatical, técnica, estrutural e consistência.

## 🚀 Funcionalidades Principais

### 🧠 Múltiplos Provedores de IA
Flexibilidade total para escolher o "cérebro" da revisão:
-   **Google Gemini**: Ótimo custo-benefício e janela de contexto massiva (padrão: `gemini-2.0-flash`).
-   **Groq**: Velocidade extrema para inferência quase instantânea (modelos Llama 3, Mixtral).
-   **OpenRouter**: Acesso a dezenas de outros modelos (GPT-4, Claude 3, Qwen, Mistral, etc.).
-   **Modo Mock**: Para testes de interface sem consumo de API.

### 🔄 Revisão Iterativa com Refinamento
Diferente de revisores comuns, este sistema **refina** o texto em camadas:
1.  O texto passa por uma primeira revisão.
2.  A saída corrigida é usada como **entrada** para a próxima iteração.
3.  O processo se repete (padrão: 5 iterações) ou até que o texto convirja (sem novos erros).
Isso permite corrigir problemas profundos que só aparecem depois que a "sujeira" superficial é limpa.

### 📊 Relatórios Consolidados
O relatório final não mostra apenas o que sobrou. Ele apresenta:
-   **Histórico Completo**: Todos os erros únicos encontrados e corrigidos durante todo o processo.
-   **Métricas**: Total de erros, tipos de erro (gramatical, técnico, estrutural), tempo de processamento e tokens consumidos.
-   **Formatos**: Disponível em **HTML** (interativo) e **Markdown**.

### 🛠️ Controle Total (GUI)
Interface gráfica moderna construída com PyQt6 que permite:
-   **Configuração Dinâmica**: Seleção de modelos via API (lista modelos disponíveis na sua conta).
-   **Ajuste Fino**: Controle de temperatura, tokens máximos, limiar de convergência (ex: parar se 95% do texto estiver ok).
-   **Persistência**: Importe/Exporte suas configurações de revisão e prompts personalizados.

---

## 🏗️ Arquitetura

Clean Architecture em 4 camadas para robustez e manutenção:

```
src/
├── core/           # Regras de Negócio (Entidades, Interfaces)
├── application/    # Casos de Uso (Orquestração da Revisão)
├── infrastructure/ # Implementações (Gateways de IA, PDF, Relatórios)
└── presentation/   # Interface Gráfica (Windows/Linux/macOS)
```

## ⚙️ Pré-requisitos

-   Python 3.10 ou superior.
-   Chave de API de pelo menos um provedor:
    -   [Google AI Studio](https://aistudio.google.com/)
    -   [Groq Cloud](https://console.groq.com/)
    -   [OpenRouter](https://openrouter.ai/)

## 📦 Instalação

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

## ▶️ Como Usar

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

## 🧪 Testes

O projeto possui alta cobertura de testes automatizados.

```bash
# Executar todos os testes
pytest tests/ -v
```

## 📄 Licença

Uso interno — todos os direitos reservados.
