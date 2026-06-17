# Árvore de Skills — NovaTech Assistant

## Foundation (3 skills — convenções globais)

| Arquivo | Frase-ativação | Criado por | Consome | Freq. |
|---|---|---|---|---|
| `skills/foundation/typescript-conventions.md` | "gere código TypeScript" / "crie um .ts" | Tech Lead | Todos os papéis + Copilot + Claude | Toda geração de código |
| `skills/foundation/error-handling.md` | "adicione tratamento de erro" / "crie custom error" | Tech Lead | Dev + Copilot | Todo novo módulo |
| `skills/foundation/project-structure.md` | "onde devo criar este arquivo?" / "configure logging" | Tech Lead | Dev + QA + Copilot | Todo novo arquivo |

> **`typescript-conventions.md` é a skill base — todas as outras dependem dela.**

---

## Domain (4 skills — padrões por camada)

| Arquivo | Frase-ativação | Criado por | Consome | Freq. |
|---|---|---|---|---|
| `skills/domain/azure-functions-endpoint.md` | "crie um endpoint" / "adicione HTTP trigger" | Tech Lead | Dev + Copilot | Cada novo endpoint |
| `skills/domain/azure-ai-search-integration.md` | "integre com Azure AI Search" / "implemente retrieval" | Tech Lead | Dev + Copilot | Pipeline RAG e SearchService |
| `skills/domain/react-components.md` | "crie um componente React" / "crie card do Teams" | Tech Lead | Dev Frontend + Copilot | Painel web e bot |
| `skills/domain/testing-patterns.md` | "escreva testes para" / "crie fixtures" | QA + Tech Lead | Dev + QA + Copilot | Todo novo módulo testado |

---

## Artifact (2 skills — receitas de geração)

| Arquivo | Frase-ativação | Criado por | Consome | Freq. |
|---|---|---|---|---|
| `skills/artifact/create-rag-endpoint.md` | "crie um endpoint RAG" / "adicione rota de [nome]" | Dev Sênior | Dev + Copilot | Cada endpoint novo (5+ no projeto) |
| `skills/artifact/create-integration-test.md` | "crie integration test para endpoint" | QA + Dev | Dev + Copilot | Um por endpoint |

> `create-react-card` foi absorvida por `react-components.md` — baixa frequência (3–5x) e `react-components` já era prescritivo o suficiente. Checklist e templates de card vivem agora na seção "Geração de cards" da skill Domain.

---

## Cadeia de dependências

```
typescript-conventions  ←── base de todas
       ↑
error-handling
project-structure
       ↑
azure-functions-endpoint  azure-ai-search-integration  react-components  testing-patterns
       ↑                         ↑                      (inclui geração        ↑
create-rag-endpoint    ←─────────┘                        de cards)   create-integration-test
```

Cada skill Artifact referencia explicitamente quais Foundation e Domain o agente deve ler antes de gerar o artefato, garantindo output consistente independente de quem (ou qual agente) executar a tarefa.

---

## Conteúdo de cada skill

### Foundation

#### `typescript-conventions.md`
- Stack obrigatória (TypeScript strict, Zod, Vitest, ESM)
- `strict: true` sem exceções — proibido `as any` e `@ts-ignore`
- Named exports obrigatórios — sem default exports
- ESM puro — extensão `.js` nos imports locais
- Zod para toda validação de input externo
- Tipos de domínio em `src/shared/types.ts` — sem redefinição local
- Convenções de nomenclatura (kebab-case arquivos, camelCase funções, PascalCase tipos)
- `logger` de `shared/logger.ts` — sem `console.log`
- `async/await` — sem `.then()` chains

#### `error-handling.md`
- Hierarquia: `AppError` → `ValidationError` | `SearchError` | `CompletionError` | `NotFoundError` | `ConfigurationError`
- Sempre lançar subclasse de `AppError` — nunca `new Error()`
- Nunca swallow errors — sempre relançar ou converter
- Mapeamento HTTP no handler, nunca no service
- Log com contexto antes de relançar
- `ZodError` → `ValidationError` no boundary de validação
- `cause` sempre preenchido quando há erro de origem

#### `project-structure.md`
- Mapa de responsabilidades: `functions/` (HTTP), `services/` (negócio), `shared/` (compartilhado)
- Handlers não contêm lógica de negócio
- Configuração de ambiente via `config.ts` — nunca `process.env` direto
- Logging via `logger.ts` (pino) — nunca `console.log`
- Testes espelham estrutura de `src/`
- Nomenclatura de arquivos por tipo

---

### Domain

#### `azure-functions-endpoint.md`
- Estrutura de três arquivos por endpoint: `handler.ts`, `validator.ts`, `response-builder.ts`
- Handler orquestra (não processa) — delega para services
- Validação em `validator.ts` separado com Zod
- Response builder monta resposta tipada com `Content-Type: application/json`
- Error handling centralizado no handler — mapeamento `AppError` → HTTP
- Health check obrigatório em todo deployment
- Contrato de response RAG: `answer`, `sources[]`, `latency_ms`

#### `azure-ai-search-integration.md`
- `SearchService` em `src/services/search.ts` com interface estável
- Retornar `SearchChunk[]` — nunca tipo nativo do SDK
- Máximo de chunks configurável via `config.maxChunks`
- Score mínimo de 0.6 para incluir chunk
- Log `warn` quando sem resultados (não silencioso)
- Em testes: fixtures de `data/retrieval-corpus/`, não Azure real

#### `react-components.md`
- Dois contextos: React JSX (painel web) e Adaptive Card JSON (Teams bot)
- Componentes são funções — nunca classes
- Props com interface TypeScript explícita
- Tipos de domínio de `src/shared/types.ts` — sem redefinição
- Um componente por arquivo
- Sem fetch dentro do componente — dados chegam via props
- Todo Adaptive Card inclui fontes e botões de feedback (requisito de negócio)
- **Seção "Geração de cards":** checklist, templates React e Adaptive Card com placeholders `{{Name}}`/`{{name}}`

#### `testing-patterns.md`
- Três categorias: `unit/` (mocks para tudo), `integration/` (MSW para APIs externas), `e2e/` (fluxo completo, com cautela)
- Estrutura de arquivos espelha `src/`
- `describe` = módulo, `it` = comportamento em linguagem natural
- Imports explícitos de vitest (`describe`, `it`, `expect`, `vi`)
- Fixtures em `tests/fixtures/` — nunca inline nos testes
- Unit tests: mock com `vi.mock`; integration tests: MSW para APIs externas
- Asserções específicas — não `toBeTruthy()` onde há asserção melhor

---

### Artifact

#### `create-rag-endpoint.md`
- Checklist de 10 itens antes de considerar completo
- Templates completos para `handler.ts`, `validator.ts`, `response-builder.ts`
- Tabela de placeholders (`{{name}}`, `{{Name}}`)
- Lista de anti-padrões a evitar na geração

#### `create-integration-test.md`
- Checklist de 9 itens (inclui todos os cenários de erro obrigatórios)
- Template MSW com mocks para Azure Search e Azure OpenAI
- Cobre: happy path, input inválido (400), falha Search (502), falha OpenAI (502)
- Instrução para verificar fixtures necessárias antes de gerar

~~`create-react-card.md`~~ — absorvida por `react-components.md` (seção "Geração de cards")
