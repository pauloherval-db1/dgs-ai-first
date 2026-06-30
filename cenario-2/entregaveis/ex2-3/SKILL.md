# Skill: TypeScript Conventions

## Contexto

Esta é a skill Foundation base. Toda geração de código TypeScript no projeto NovaTech deve seguir estas regras.

Aplica-se a qualquer artefato:
- handlers de Azure Functions
- services
- componentes React
- testes unitários e de integração

As skills de Domain e Artifact dependem desta.

Frase-ativação:
- gere código TypeScript para o projeto NovaTech
- crie um novo arquivo .ts
- implemente qualquer funcionalidade em TypeScript

## Rastreabilidade com decisões do Cenário 1 (ADRs)

- ADR-0001 (LLM Azure OpenAI GPT-4o): todo contrato de código deve manter compatibilidade com integrações Azure e tipagem explícita para requests/responses.
- ADR-0002 (context budget): estruturas de payload e tipos de prompt devem permitir controle de orçamento de contexto por campo (system, chunks, pergunta, histórico).
- ADR-0003 (documentos contraditórios): tipos de domínio e respostas devem suportar metadado de vigência e rastreabilidade de fonte.
- ADR-0004 (lições do protótipo open-source): contratos devem ser estáveis e testáveis para evoluir chunking/retrieval sem quebrar handlers.

### Regras derivadas dos ADRs

- Toda resposta de endpoint deve manter rastreabilidade de fonte (`source_document` e/ou `sources[]`).
- Tipos de retrieval devem carregar metadados mínimos: `documentId`, `version`, `effectiveDate`, `score`.
- Configuração de limites de contexto deve ficar em arquivo de config tipado; não usar números mágicos no código.
- Mudança em tipos compartilhados exige atualização de testes e validações Zod no mesmo commit.

---

## Regras prescritivas

### 1) Strict mode obrigatório, sem atalhos

Nunca usar `as any` e nunca usar `// @ts-ignore`.

**DON'T**
```typescript
const payload = req.body as any;
// @ts-ignore
const customerId = payload.customer_id;
```

**DO**
```typescript
import { z } from "zod";

const requestSchema = z.object({
  customerId: z.string().min(1),
  message: z.string().min(1)
});

type RequestBody = z.infer<typeof requestSchema>;

export function parseRequestBody(input: unknown): RequestBody {
  return requestSchema.parse(input);
}
```

### 2) Named exports somente

Não usar default export.

**DON'T**
```typescript
export default class SearchService {
  run(): void {}
}
```

**DO**
```typescript
export class SearchService {
  run(): void {}
}
```

### 3) ESM puro com .js nos imports locais

Todo import local deve terminar com `.js`.

**DON'T**
```typescript
import { SearchService } from "../services/search-service";
import type { QueryRequest } from "../shared/types";
```

**DO**
```typescript
import { SearchService } from "../services/search-service.js";
import type { QueryRequest } from "../shared/types.js";
```

### 4) Validação de input externo com Zod

Qualquer entrada de HTTP, Teams ou arquivo externo deve ser validada antes do uso.

**DON'T**
```typescript
import type { HttpRequest } from "@azure/functions";
import type { QueryRequest } from "../../shared/types.js";

export function extractQuery(req: HttpRequest): QueryRequest {
  return req.body as QueryRequest;
}
```

**DO**
```typescript
import type { HttpRequest } from "@azure/functions";
import { queryRequestSchema } from "../../shared/types.js";
import type { QueryRequest } from "../../shared/types.js";

export async function extractQuery(req: HttpRequest): Promise<QueryRequest> {
  const body = await req.json();
  return queryRequestSchema.parse(body);
}
```

### 5) Tipos de domínio centralizados em src/shared/types.ts

Tipos compartilhados não devem ser redefinidos em handlers/services.

**DON'T**
```typescript
// src/functions/query/handler.ts
interface QueryRequest {
  question: string;
  session_id?: string;
}
```

**DO**
```typescript
// src/functions/query/handler.ts
import type { QueryRequest } from "../../shared/types.js";
```

### 6) Convenções de nomenclatura obrigatórias

- arquivos: kebab-case.ts
- funções, variáveis e objetos: camelCase
- classes e tipos: PascalCase
- constantes de módulo: UPPER_SNAKE_CASE
- schemas Zod: camelCase + Schema

**DON'T**
```typescript
const maxChunks = 5;
const Query_Request_Schema = z.object({ question: z.string() });
const request_payload = { customer_id: "123" };

function BuildResponse(): void {}
```

**DO**
```typescript
const MAX_CHUNKS = 5;
const queryRequestSchema = z.object({ question: z.string() });
const requestPayload = { customerId: "123" };

function buildResponse(): void {}
```

### 7) Proibido console.log, usar logger do projeto

Usar `src/shared/logger.ts` para logs estruturados.

**DON'T**
```typescript
console.log("Received query", question);
console.error("Search failed", error);
```

**DO**
```typescript
import { logger } from "../../shared/logger.js";

logger.info({ question }, "Received query");
logger.error({ err: error }, "Search failed");
```

### 8) Fluxo assíncrono com legibilidade e sem await excessivo

Use `async/await` como padrão para fluxos com validação, branching e tratamento de erro.
`then` pode ser usado em transformações curtas e lineares.

**DON'T**
```typescript
const profile = await userService.getProfile(userId);
const settings = await userService.getSettings(userId);
return await buildUserView(profile, settings);
```

**DO**
```typescript
const [profile, settings] = await Promise.all([
  userService.getProfile(userId),
  userService.getSettings(userId)
]);
return buildUserView(profile, settings);
```

**DO (then aceitável em pipeline curto)**
```typescript
return searchService
  .search(query)
  .then((chunks) => chunks.slice(0, 5))
  .then((topChunks) => buildPrompt(topChunks));
```

### 9) Tratamento de erro explícito, sem erro genérico

Evite `throw new Error("something went wrong")` sem contexto. Use `try/catch` quando houver IO/chamadas externas e retorne erros específicos com metadados úteis.

**DON'T**
```typescript
export async function loadCustomer(customerId: string): Promise<Customer> {
  const response = await httpClient.get(`/customers/${customerId}`);
  if (!response.ok) {
    throw new Error("Request failed");
  }
  return response.data as Customer;
}
```

**DO**
```typescript
class CustomerNotFoundError extends Error {
  constructor(customerId: string) {
    super(`Customer not found: ${customerId}`);
    this.name = "CustomerNotFoundError";
  }
}

class ExternalServiceError extends Error {
  constructor(serviceName: string, details: string) {
    super(`${serviceName} call failed: ${details}`);
    this.name = "ExternalServiceError";
  }
}

export async function loadCustomer(customerId: string): Promise<Customer> {
  try {
    const response = await httpClient.get(`/customers/${customerId}`);
    if (response.status === 404) {
      throw new CustomerNotFoundError(customerId);
    }
    if (!response.ok) {
      throw new ExternalServiceError("CustomerAPI", `status=${response.status}`);
    }
    return response.data as Customer;
  } catch (error) {
    if (error instanceof CustomerNotFoundError) {
      throw error;
    }
    throw new ExternalServiceError("CustomerAPI", String(error));
  }
}
```

---

## Exemplos concretos

### Handler HTTP com validação, logger e tipos compartilhados

```typescript
import type { HttpRequest, HttpResponseInit, InvocationContext } from "@azure/functions";
import { queryRequestSchema, type QueryRequest } from "../../shared/types.js";
import { logger } from "../../shared/logger.js";
import { runQuery } from "../../services/query-service.js";

export async function queryHandler(
  req: HttpRequest,
  _context: InvocationContext
): Promise<HttpResponseInit> {
  const body = await req.json();
  const input: QueryRequest = queryRequestSchema.parse(body);

  logger.info({ question: input.question }, "Received query request");

  const answer = await runQuery(input);

  return {
    status: 200,
    jsonBody: {
      answer,
      sessionId: input.sessionId ?? null
    }
  };
}
```

### Teste Vitest realista para validação de schema

```typescript
import { describe, expect, it } from "vitest";
import { queryRequestSchema } from "../../src/shared/types.js";

describe("queryRequestSchema", () => {
  it("aceita payload válido", () => {
    const parsed = queryRequestSchema.parse({
      question: "Qual o prazo de entrega para RJ?",
      sessionId: "abc-123"
    });

    expect(parsed.question).toBe("Qual o prazo de entrega para RJ?");
    expect(parsed.sessionId).toBe("abc-123");
  });

  it("rejeita payload sem question", () => {
    expect(() =>
      queryRequestSchema.parse({
        sessionId: "abc-123"
      })
    ).toThrow();
  });
});
```

---

## Anti-padrões úteis

- Uso de `as any` em payload externo: remove proteção do TypeScript e mascara bugs de contrato.
- Uso de `// @ts-ignore`: esconde erro de design de tipos em vez de corrigi-lo.
- Default export em handlers/services: dificulta refactor e auto-import.
- Imports locais sem `.js`: quebra consistência ESM no build e em ferramentas.
- Tipos duplicados em módulos diferentes: gera deriva de contrato entre camadas.
- `console.log` em produção: logs não estruturados e fora do pipeline padrão de observabilidade.
- Uso excessivo de `await` sequencial para operações independentes: piora latência.
- Fluxo assíncrono inconsistente (mistura confusa de `then` e `await`): dificulta manutenção.
- Erro genérico sem contexto (`new Error("Request failed")`): reduz rastreabilidade e resposta operacional.
- Schema Zod não reutilizado de `src/shared/types.ts`: duplica regra de validação e cria inconsistências.

---

## Dependências

Nenhuma. Esta é a skill base para todo código TypeScript do projeto.
