# 📋 Revisor de Textos Estruturados

Sistema de revisão automática de textos estruturados usando inteligência artificial (Google Gemini).

## 🎯 Funcionalidades

- **Revisão Gramatical**: Ortografia, concordância, regência, pontuação
- **Revisão Técnica**: Terminologia pericial, conformidade com normas
- **Revisão Estrutural**: Organização lógica, coerência entre seções
- **Verificação de Consistência**: Cruzamento entre seções do documento
- **Relatórios**: Geração em Markdown e HTML com métricas detalhadas
- **Interface Gráfica**: GUI PyQt6 moderna com tema profissional

## 🏗️ Arquitetura

Clean Architecture em 4 camadas:

```
src/
├── core/           # Domínio: entidades, enums, exceções, interfaces
├── application/    # Casos de uso e orquestração
├── infrastructure/ # IA (Gemini), PDF, relatórios, repositórios
└── presentation/   # GUI PyQt6
```

## ⚙️ Requisitos

- Python 3.10+
- API key do Google Gemini

## 🚀 Instalação

```bash
# Clonar o repositório
git clone <repo-url>
cd revisor_textos

# Instalar dependências
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env e definir GEMINI_API_KEY
```

## ▶️ Uso

```bash
# Executar a aplicação
python main.py
```

### Modo Mock (sem API key)

A aplicação funciona em **modo mock** sem a API key configurada, útil para desenvolvimento e testes da interface.

## 🧪 Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ -v --tb=short
```

## 📁 Estrutura de Diretórios

```
revisor_textos/
├── main.py                  # Ponto de entrada
├── requirements.txt         # Dependências
├── .env.example             # Template de configuração
├── src/
│   ├── core/
│   │   ├── entities/        # Laudo, Secao, Revisao, Erro...
│   │   ├── enums/           # StatusLaudo, TipoErro...
│   │   ├── exceptions/      # Hierarquia de exceções
│   │   ├── interfaces/      # Contratos (repositories, services, gateways)
│   │   ├── validators/      # Validadores de negócio
│   │   └── value_objects/   # LocalizacaoErro, MetadadosPDF...
│   ├── application/
│   │   ├── dto/             # Data Transfer Objects
│   │   ├── use_cases/       # ProcessarLaudo, RevisarSecao...
│   │   └── services/        # OrquestradorRevisao
│   ├── infrastructure/
│   │   ├── ai/              # GeminiGateway, PromptBuilder, Agentes
│   │   ├── pdf/             # PdfProcessor (PyPDF2)
│   │   ├── reports/         # Geradores Markdown e HTML
│   │   ├── repositories/    # Persistência JSON
│   │   └── logging/         # AppLogger
│   └── presentation/
│       ├── main_window.py   # Janela principal
│       ├── tema.py          # Sistema de tema/estilos
│       ├── widgets/         # ProgressoWidget, ResultadosWidget
│       ├── controllers/     # ControladorPrincipal
│       └── dialogs/         # ConfigDialog
└── tests/                   # Testes unitários
```

## 🔧 Configuração

Edite o arquivo `.env` ou use o menu **Configurações > Preferências** na GUI:

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `GEMINI_API_KEY` | — | Chave da API Gemini |
| `gemini_model` | `gemini-2.0-flash` | Modelo de IA |
| `max_iteracoes` | `5` | Iterações por seção |
| `limiar_convergencia` | `0.95` | Limiar para parar revisão |
| `temperatura_revisao` | `0.3` | Temperatura do modelo |

## 📄 Licença

Uso interno — todos os direitos reservados.
