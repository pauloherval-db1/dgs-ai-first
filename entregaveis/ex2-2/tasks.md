# Tasks — Query Endpoint

> Gerado a partir de `specs/query-endpoint/plan.md`
> Módulo: `src/functions/query/` + `src/services/`
> Stack: TypeScript · Azure Functions v4 · Zod · pino

---

## QE-001 — Tipos de domínio compartilhados

**Descrição:** Criar os tipos TypeScript do domínio do query endpoint em `src/shared/types.ts`: `QueryRequest`, `QueryResponse`, `SearchChunk`, `SourceDocument`.

**Critérios de aceite:**
- `QueryRequest` valida `question: string` e `session_id?: string`
- `QueryResponse` inclui `answer: string`, `sources: SourceDocument[]`, `latency_ms: number`
- `SearchChunk` inclui `content: string`, `source_document: SourceDocument`, `score: number`
- `SourceDocument` inclui `title: string`, `url: string`, `vigency?: string` (metadado ADR-0003)
- Arquivo compila sem erros com `strict: true`

**Dependências:** nenhuma

**Estimativa:** P

---

## QE-002 — Configuração de ambiente

**Descrição:** Adicionar as variáveis de ambiente do query endpoint em `src/shared/config.ts`: conexão com Azure AI Search e Azure OpenAI (embeddings + completion).

**Critérios de aceite:**
- Variáveis cobertas: `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX`, `AZURE_SEARCH_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_COMPLETION_DEPLOYMENT`
- Leitura falha em startup com erro descritivo se variável obrigatória estiver ausente
- Config é lida uma única vez e exportada como objeto imutável
- Arquivo compila sem erros com `strict: true`

**Dependências:** nenhuma

**Estimativa:** P

---

## QE-003 — Validador de input (Zod)

**Descrição:** Implementar `src/functions/query/validator.ts` com schema Zod que valida o body da requisição POST `/api/query`.

**Critérios de aceite:**
- Schema valida `question` como string não-vazia com max 1000 caracteres
- Schema valida `session_id` como string opcional
- Retorna erro `400` com mensagem legível para input inválido (question vazia, question excedendo limite)
- Testes unitários em `tests/unit/query/validator.test.ts` cobrem: campo ausente, vazio, limite de caracteres, payload válido
- Zero chamadas externas no teste (sem mock de rede)

**Dependências:** QE-001

**Estimativa:** P

---

## QE-004 — Serviço de embedding

**Descrição:** Implementar `src/services/search.ts` — função `generateEmbedding(question: string): Promise<number[]>` que chama Azure OpenAI Embeddings.

**Critérios de aceite:**
- Usa o deployment configurado em `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- Implementa retry com exponential backoff (3 tentativas, delays: 500ms / 1000ms / 2000ms) para erros 429 e 5xx
- Loga tentativas e falhas via `src/shared/logger.ts` (pino)
- Lança `EmbeddingError` (de `src/shared/errors.ts`) após esgotar retries
- Testes unitários em `tests/unit/services/search.test.ts` usam mock da chamada HTTP e cobrem: sucesso, retry em 429, falha após 3 tentativas

**Dependências:** QE-001, QE-002

**Estimativa:** M

---

## QE-005 — Serviço de busca vetorial

**Descrição:** Implementar a função `searchChunks(embedding: number[], topK: number): Promise<SearchChunk[]>` em `src/services/search.ts` que consulta o Azure AI Search.

**Critérios de aceite:**
- Usa vector search no índice configurado em `AZURE_SEARCH_INDEX`
- Retorna até `topK` chunks ordenados por score decrescente (default `topK = 5`)
- Cada chunk retornado é mapeado para `SearchChunk` (QE-001)
- Implementa retry com exponential backoff (mesma política de QE-004)
- Loga a query, quantidade de resultados e latência
- Testes unitários cobrem: resposta com 5 chunks, resposta vazia, erro de rede com retry

**Dependências:** QE-001, QE-002, QE-004

**Estimativa:** M

---

## QE-006 — Prompt builder

**Descrição:** Implementar `src/services/prompt-builder.ts` — monta o prompt final respeitando o context budget definido na ADR-0002 (~4K tokens para system prompt + ~8K tokens para chunks).

**Critérios de aceite:**
- Lê o system prompt de `/prompts/system-prompt.md` em tempo de execução
- Monta o prompt na ordem: system prompt → chunks (com título da fonte e metadado de vigência) → pergunta do usuário
- Trunca chunks que excedam o budget de 8K tokens, priorizando os de maior score
- Função pura e testável: recebe `systemPrompt`, `chunks: SearchChunk[]`, `question` e retorna `string`
- Testes unitários cobrem: budget respeitado com 5 chunks, truncagem quando chunks excedem 8K, chunks com metadado de vigência incluídos corretamente

**Dependências:** QE-001, QE-005

**Estimativa:** M

---

## QE-007 — Serviço de completion (GPT-4o)

**Descrição:** Implementar `src/services/completion.ts` — função `getCompletion(prompt: string): Promise<string>` que chama Azure OpenAI Chat Completions com o modelo GPT-4o.

**Critérios de aceite:**
- Usa o deployment configurado em `AZURE_OPENAI_COMPLETION_DEPLOYMENT`
- Implementa retry com exponential backoff (mesma política de QE-004)
- Loga tokens usados (prompt tokens, completion tokens) via pino
- Lança `CompletionError` (de `src/shared/errors.ts`) após esgotar retries
- Testes unitários cobrem: resposta bem-sucedida, retry em 429, falha após 3 tentativas

**Dependências:** QE-001, QE-002

**Estimativa:** M

---

## QE-008 — Response builder

**Descrição:** Implementar `src/functions/query/response-builder.ts` — monta o `QueryResponse` final a partir da resposta do modelo e dos chunks recuperados.

**Critérios de aceite:**
- Extrai `sources: SourceDocument[]` dos `SearchChunk[]` usados no prompt (sem duplicatas)
- Calcula `latency_ms` (tempo total da requisição)
- Garante que a resposta nunca cite fonte fora dos `SearchChunk[]` recebidos
- Retorna `QueryResponse` tipado (QE-001)
- Testes unitários cobrem: deduplicação de fontes, cálculo de latência, mapeamento correto de campos

**Dependências:** QE-001, QE-005, QE-007

**Estimativa:** P

---

## QE-009 — HTTP handler da Azure Function

**Descrição:** Implementar `src/functions/query/handler.ts` — HTTP trigger da Azure Function que orquestra todo o fluxo POST `/api/query`.

**Critérios de aceite:**
- Registra a função com `app.http('query', { methods: ['POST'], authLevel: 'function', handler })`
- Fluxo: validar input → gerar embedding → buscar chunks → montar prompt → obter completion → montar resposta
- Retorna `200` com `QueryResponse` serializado em JSON
- Retorna `400` para input inválido (do validador QE-003)
- Retorna `500` com mensagem genérica para erros internos (não expõe stack trace)
- Loga início, fim e erros da requisição com `session_id` e latência (pino)
- Testes de integração em `tests/integration/query/handler.test.ts` usam mocks para Azure AI Search e Azure OpenAI (msw) e cobrem: fluxo completo com sucesso, input inválido, falha no serviço de busca, falha no completion

**Dependências:** QE-003, QE-004, QE-005, QE-006, QE-007, QE-008

**Estimativa:** G

---

## QE-010 — Health check endpoint

**Descrição:** Implementar `src/functions/health/handler.ts` — endpoint GET `/api/health` que confirma que a função está ativa.

**Critérios de aceite:**
- Retorna `200 OK` com `{ status: "ok", timestamp: "<ISO8601>" }`
- Não faz chamadas externas (sem validação de conectividade nesta versão)
- Registrado como Azure Function HTTP trigger
- Teste unitário cobre resposta `200` com campos obrigatórios

**Dependências:** QE-002

**Estimativa:** P

---

## QE-011 — Custom errors

**Descrição:** Definir as classes de erro customizadas do módulo em `src/shared/errors.ts`: `EmbeddingError`, `SearchError`, `CompletionError`, `ValidationError`.

**Critérios de aceite:**
- Cada classe estende `Error` e inclui `statusCode: number` e `cause?: unknown`
- `ValidationError` carrega `field?: string` para indicar qual campo falhou
- Arquivo compila sem erros com `strict: true`
- Utilizado consistentemente por QE-004, QE-005, QE-007

**Dependências:** nenhuma

**Estimativa:** P

---

## Resumo de dependências

```
QE-001 ──┬──> QE-003 ──┐
          │              │
QE-002 ──┼──> QE-004 ──┼──> QE-005 ──┬──> QE-006 ──┐
          │              │              │              ├──> QE-009
          └──> QE-007 ──┴──────────────┴──> QE-008 ──┘
QE-011 ──> (QE-004, QE-005, QE-007 consomem)
QE-010 ──> independente após QE-002
```

## Ordem sugerida de implementação

| Sprint | Tasks | Racional |
|--------|-------|----------|
| 1 | QE-001, QE-002, QE-011 | Fundação: tipos, config, erros |
| 2 | QE-003, QE-004, QE-010 | Validação e primeiro serviço externo + health |
| 3 | QE-005, QE-007 | Busca vetorial e completion em paralelo |
| 4 | QE-006, QE-008 | Prompt builder e response builder |
| 5 | QE-009 | Integração final + testes de integração |
