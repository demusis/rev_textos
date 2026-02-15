# 📋 Revisor de Textos Estruturados

Sistema de revisão automática de textos estruturados usando inteligência artificial (Google Gemini).

O sistema processa documentos (PDF, Markdown), identifica seções e aplica múltiplos ciclos de revisão para garantir qualidade gramatical, técnica e consistência.

## 🎯 Funcionalidades Principais

-   **Revisão Iterativa com Refinamento**: O sistema não apenas aponta erros, mas refina o texto em ciclos (padrão: 5 iterações). A correção de uma iteração serve de entrada para a próxima, permitindo correções em camadas (do gramatical ao estilístico).
-   **Consolidação de Erros**: O relatório final apresenta **todos** os erros únicos encontrados durante todo o processo, garantindo que o histórico completo de correções seja visível.
-   **Verificação de Convergência**: O sistema detecta automaticamente quando o texto está "pronto" (quando novos erros param de aparecer) e encerra o ciclo de revisão antecipadamente para economizar recursos.
-   **Múltiplos Agentes Especializados**:
    -   **Revisor Gramatical**: Foca em correção linguística.
    -   **Revisor Técnico**: Verifica terminologia e normas.
    -   **Validador**: Confere se as correções propostas são seguras.
    -   **Consistência**: Analisa contradições entre diferentes seções do documento.

## 🏗️ Arquitetura

Clean Architecture em 4 camadas:

```
src/
├── core/           # Domínio: entidades, enums, exceções
├── application/    # Casos de uso (Orquestrador, RevisarSecao...)
├── infrastructure/ # Implementações (Gemini, PDF, Repositórios)
└── presentation/   # GUI PyQt6 (Windows/Linux/macOS)
```

## ⚙️ Requisitos

-   Python 3.10+
-   Chave de API do Google Gemini (gratuita ou paga)

## 🚀 Instalação

1.  **Clonar o repositório**
    ```bash
    git clone https://github.com/demusis/rev_textos.git
    cd rev_textos
    ```

2.  **Instalar dependências**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar Variáveis de Ambiente**
    Copie o arquivo de exemplo e edite com sua chave:
    ```bash
    cp .env.example .env
    # Abra o .env e insira sua GEMINI_API_KEY
    ```

## ▶️ Uso

Execute o arquivo principal para abrir a interface gráfica:

```bash
python main.py
```

### Fluxo de Trabalho
1.  **Carregar**: Arraste um PDF ou arquivo de texto para a área de upload.
2.  **Configurar**: Ajuste o nível de criatividade (temperatura) ou o número máximo de iterações no menu de configurações.
3.  **Analisar**: Clique em "Iniciar Revisão". O sistema dividirá o texto em seções e iniciará os agentes.
4.  **Acompanhar**: Veja o progresso em tempo real, incluindo o número de erros encontrados em cada iteração.
5.  **Resultado**: Ao final, um relatório completo (HTML/Markdown) será gerado na pasta `output/`.

## 🧪 Testes

O projeto conta com uma suíte de testes automatizados:

```bash
# Executar todos os testes
pytest tests/ -v
```

## 📁 Estrutura de Diretórios

```
revisor_textos/
├── main.py                  # Launcher
├── src/                     # Código fonte
├── tests/                   # Testes unitários e de integração
├── config/                  # Arquivos de configuração JSON
├── logs/                    # Logs de execução
└── output/                  # Relatórios gerados
```

## 📄 Licença

Uso interno — todos os direitos reservados.
