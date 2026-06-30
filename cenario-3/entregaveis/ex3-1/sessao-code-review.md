# Exercício 3.1 — Structured Output e Guardrails Determinísticos
## Registro de sessão: Code Review com Claude

**Papel:** Desenvolvedor  
**Tópico:** Harness Engineering — Structured Outputs e verificações determinísticas  
**Arquivo central:** `novatech-assistant/src/services/response-validator.ts`  
**Data:** 2026-06-29

---

## Contexto do exercício

Implementar um `response-validator.ts` que:
1. Valide respostas do assistente contra um schema Zod (structured output)
2. Aplique 2 guardrails determinísticos que complementam o prompt probabilístico

**Guardrails a implementar:**
1. *"Toda resposta DEVE conter o campo `source_document` — se não tiver, a resposta é rejeitada e substituída por mensagem padrão."*
2. *"Respostas que mencionam 'carga perigosa' junto com 'devolução' DEVEM conter a negativa — se afirmarem que a devolução é possível, a resposta é bloqueada."*

---

## Prompt 1 — Code Review do artefato gerado pelo Copilot

**Critérios de avaliação solicitados:**
- O schema de structured output é válido e usa Zod corretamente?
- Os 2 guardrails realmente bloqueiam respostas inválidas (não apenas logam)?
- O code review identifica problemas reais (não inventados)?
- A distinção entre prompt (probabilístico) e código (determinístico) fica clara?

### Arquivos analisados

**`structured-output.schema.ts` (gerado pelo Copilot):**
```typescript
import { z } from "zod";

export const structuredOutputSchema = z
    .object({
        answer: z.string().trim().min(1, "answer must not be empty"),
        source_document: z.string().trim().min(1, "source_document must not be empty"),
        confidence_score: z
            .number({ invalid_type_error: "confidence_score must be a number" })
            .min(0, "confidence_score must be between 0 and 1")
            .max(1, "confidence_score must be between 0 and 1"),
    })
    .strict();

export type StructuredOutput = z.infer<typeof structuredOutputSchema>;
```

**`response-validator.ts` — v1 (gerado pelo Copilot):**
```typescript
import {
    structuredOutputSchema,
    type StructuredOutput,
} from "./structured-output.schema";

const guardrailMessage =
    "Não foi possível responder com segurança com base na documentação oficial. Encaminhe para revisão humana.";

export type RejectionReason =
    | "schema_validation_failed"
    | "missing_source_document"
    | "dangerous_cargo_return_without_negative";

export interface ValidationResult {
    accepted: boolean;
    reason?: RejectionReason;
    response: StructuredOutput;
}

export type ValidatorLogger = (reason: RejectionReason, details?: string) => void;

const safeFallbackResponse: StructuredOutput = {
    answer: guardrailMessage,
    source_document: "SYSTEM-GUARDRAIL",
    confidence_score: 0,
};

export function validateAssistantResponse(
    rawResponse: unknown,
    logger: ValidatorLogger = () => undefined,
): ValidationResult {
    const parsed = structuredOutputSchema.safeParse(rawResponse);

    if (!parsed.success) {
        logger("schema_validation_failed", parsed.error.issues.map((issue) => issue.message).join("; "));
        return { accepted: false, reason: "schema_validation_failed", response: safeFallbackResponse };
    }

    const response = parsed.data;

    // GUARDRAIL 1
    if (!response.source_document.trim()) {
        logger("missing_source_document", "source_document field is empty after trim");
        return { accepted: false, reason: "missing_source_document", response: safeFallbackResponse };
    }

    // GUARDRAIL 2
    if (violatesDangerousCargoReturnGuardrail(response.answer)) {
        logger("dangerous_cargo_return_without_negative", "...");
        return { accepted: false, reason: "dangerous_cargo_return_without_negative", response: safeFallbackResponse };
    }

    return { accepted: true, response };
}

function violatesDangerousCargoReturnGuardrail(answer: string): boolean {
    const normalized = normalize(answer);
    const mentionsDangerousCargo = /\bcargas?\s+perigosas?\b/.test(normalized);
    const mentionsReturn = /\bdevoluc(?:ao|oes)\b|\bdevolver\b|\bdevolvid[oa]s?\b/.test(normalized);

    if (!mentionsDangerousCargo || !mentionsReturn) return false;

    const hasNegativeSignal =
        /\bnao\s+pod(?:e|em)\b/.test(normalized) ||
        /\bnao\s+e\s+possivel\b/.test(normalized) ||
        /\bnao\s+sao\s+elegiveis\b/.test(normalized) ||
        /\bproibid[oa]s?\b/.test(normalized) ||
        /\bvedad[oa]s?\b/.test(normalized) ||
        /\bineligiveis?\b/.test(normalized);

    return !hasNegativeSignal;
}

function normalize(text: string): string {
    return text.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

export const safeResponseFallback = safeFallbackResponse;
```

---

### Resposta 1 — Code Review

#### 1. Schema Zod — Válido e correto? ✅ Sim, com ressalva

O schema em `structured-output.schema.ts` está bem escrito:
- `.strict()` rejeita campos extras corretamente
- `answer` e `source_document` com `.trim().min(1)` — nunca aceita string vazia
- `confidence_score` com `.number().min(0).max(1)` — range correto
- `z.infer<typeof structuredOutputSchema>` para tipagem — uso correto

A ressalva é que o `.trim().min(1)` no `source_document` cria um efeito colateral no guardrail 1.

#### 2. Os 2 guardrails realmente bloqueiam? ⚠️ Sim, mas um tem dead code

**Guardrail 1 — `source_document` ausente:** Bloqueia, mas pelo caminho errado. O `safeParse` rejeita a resposta com `schema_validation_failed` antes de chegar nas linhas do check explícito, porque o schema já impõe `.trim().min(1)`. O bloco `missing_source_document` é **código morto** — nunca executa. O próprio teste confirma isso ao esperar `"schema_validation_failed"`, não `"missing_source_document"`. O tipo `RejectionReason` declara um estado que nunca ocorre.

**Guardrail 2 — carga perigosa + devolução:** Bloqueia deterministicamente e retorna o `safeFallbackResponse`. A lógica está correta no caminho feliz, mas com problemas de cobertura de regex.

#### 3. Code Review — 4 problemas reais identificados

**Problema 1 — `missing_source_document` é dead code (alto impacto)**

O schema `source_document: z.string().trim().min(1)` já garante que strings vazias ou nulas falham o `safeParse`. O bloco abaixo nunca é alcançado:

```typescript
if (!response.source_document.trim()) {   // ← nunca true após safeParse bem-sucedido
    logger("missing_source_document", ...);
    return { accepted: false, reason: "missing_source_document", ... };
}
```

Consequência: a distinção semântica entre "schema inválido" e "source_document ausente" está quebrada. A `RejectionReason` descreve um estado que nunca ocorre.

**Problema 2 — Regex de "carga perigosa" com cobertura estreita (médio impacto)**

```typescript
const mentionsDangerousCargo = /\bcargas?\s+perigosas?\b/.test(normalized);
```

Só captura a frase literal. Um modelo que use "produto perigoso", "mercadoria perigosa", "material perigoso", ou que referencie "classe 3 da ANTT" sem a frase exata, escapa do guardrail.

**Problema 3 — Sinais negativos incompletos (médio impacto)**

Os padrões cobrem "não pode/podem", "não é possível", "proibido", "vedado", "inelegíveis". Faltam: "impossível", "não é permitido/a", "não se aplica", "excluído". Um modelo que use essas alternativas produz um **falso negativo**: a resposta errada passa pelo guardrail.

**Problema 4 — Naming inconsistente no export (baixo impacto)**

```typescript
const safeFallbackResponse: StructuredOutput = { ... };   // interna
export const safeResponseFallback = safeFallbackResponse;  // export com nome invertido
```

O mesmo objeto tem dois nomes com ordem de palavras invertida, causando confusão desnecessária.

#### 4. Distinção prompt (probabilístico) vs código (determinístico)

Na prática a distinção existe — o `response-validator.ts` é código determinístico puro. Mas no artefato, essa distinção não está articulada: não há comentário que explique "este módulo existe porque o prompt não garante conformidade de formato". Um comentário de cabeçalho resolve.

#### Resumo do review

| Critério | Status |
|---|---|
| Schema Zod válido e correto | ✅ Correto |
| Guardrail 1 bloqueia (não só loga) | ⚠️ Bloqueia via schema, mas `missing_source_document` é dead code |
| Guardrail 2 bloqueia (não só loga) | ✅ Bloqueia, mas regex tem gaps reais |
| Code review com problemas reais | ✅ 4 problemas reais, nenhum inventado |
| Distinção probabilístico vs determinístico | ⚠️ Existe na prática, mas não está documentada no artefato |

---

## Prompt 2 — Aplicar correções (v1 → v2)

> Renomeie esse arquivo para `response-validator.v1.ts` e crie um novo `response-validator.ts` com as correções informadas.

### Resposta 2 — Correções aplicadas (v2)

Arquivo original renomeado para `response-validator.v1.ts`. Novo `response-validator.ts` criado com as seguintes correções:

**Correção 1 — Dead code removido:** bloco `missing_source_document` eliminado. `RejectionReason` não declara mais um estado que nunca ocorre. Comentário explica o motivo.

**Correção 2 — Regex de "carga perigosa" expandido:**
```typescript
const mentionsDangerousCargo =
    /\bcargas?\s+perigosas?\b/.test(normalized) ||
    /\bprodutos?\s+perigosos?\b/.test(normalized) ||
    /\bmercadorias?\s+perigosas?\b/.test(normalized) ||
    /\bmateriais?\s+perigosos?\b/.test(normalized) ||
    /\bclasses?\s+\d.*\bantt\b/.test(normalized);
```

**Correção 3 — Sinais negativos expandidos:**
```typescript
const hasNegativeSignal =
    /\bnao\s+pod(?:e|em)\b/.test(normalized) ||
    /\bnao\s+e\s+possivel\b/.test(normalized) ||
    /\bnao\s+sao\s+elegiveis\b/.test(normalized) ||
    /\bnao\s+e\s+permitid[oa]s?\b/.test(normalized) ||   // novo
    /\bnao\s+se\s+aplica\b/.test(normalized) ||           // novo
    /\bimpossivel\b/.test(normalized) ||                  // novo
    /\bproibid[oa]s?\b/.test(normalized) ||
    /\bvedad[oa]s?\b/.test(normalized) ||
    /\bineligiveis?\b/.test(normalized) ||
    /\bexcluidos?\b/.test(normalized);                    // novo
```

**Correção 4 — Naming unificado:** `safeFallbackResponse` exportado diretamente, re-export `safeResponseFallback` removido. Teste atualizado para o novo nome.

**Correção 5 — Comentário de cabeçalho:** articula explicitamente a distinção probabilístico (prompt) vs determinístico (este módulo).

---

## Prompt 3 — O schema aceita campos extras?

> o schema aceita campos extras?

### Resposta 3

Não. O schema usa `.strict()` na linha 12 de `structured-output.schema.ts`. O `.strict()` do Zod faz o parse falhar se o objeto contiver qualquer campo além dos declarados. Há um teste cobrindo exatamente isso:

```typescript
it("rejects payloads with extra fields", () => {
    expect(() =>
        structuredOutputSchema.parse({
            answer: "ok",
            source_document: "POL-001",
            confidence_score: 0.8,
            extra: true,   // ← campo extra
        }),
    ).toThrow();
});
```

Este ponto do code review do exercício já estava correto e coberto.

---

## Prompt 4 — O regex de "carga perigosa + devolução" cobre variações?

> o regex de "carga perigosa + devolução" cobre variações?

### Resposta 4

Parcialmente — melhorou com as correções do v2, mas havia uma lacuna crítica no lado da "devolução":

**O que o v2 cobria:**

| Regex | Captura |
|---|---|
| `\bcargas?\s+perigosas?\b` | carga perigosa, cargas perigosas |
| `\bprodutos?\s+perigosos?\b` | produto perigoso |
| `\bmercadorias?\s+perigosas?\b` | mercadoria perigosa |
| `\bmateriais?\s+perigosos?\b` | material perigoso |
| `\bclasses?\s+\d.*\bantt\b` | classe 3 da ANTT |
| `\bdevoluc(?:ao\|oes)\b` | devolução, devoluções |
| `\bdevolver\b` | devolver |
| `\bdevolvid[oa]s?\b` | devolvida, devolvido |

**Gap crítico identificado:** o lado da devolução não cobria "retorno" e "reenvio", sinônimos comuns em contexto logístico. Uma resposta como *"O retorno de cargas perigosas é possível mediante autorização"* passaria pelo guardrail sem ser bloqueada.

---

## Prompt 5 — Aplicar correção do retorno/reenvio (v2 → v3)

> Faça a correção, e renomeie esse arquivo para `response-validator.v2.ts` e crie um novo `response-validator.ts` com as correções informadas.

### Resposta 5 — Correção aplicada (v3)

Arquivo renomeado para `response-validator.v2.ts`. Único delta em relação ao v2:

```typescript
// Expanded to cover "retorno" and "reenvio", common logistics synonyms for devolução.
const mentionsReturn =
    /\bdevoluc(?:ao|oes)\b|\bdevolver\b|\bdevolvid[oa]s?\b/.test(normalized) ||
    /\bretorno\b/.test(normalized) ||
    /\breenvio\b/.test(normalized);
```

---

## Artefatos produzidos

| Arquivo | Descrição |
|---|---|
| `src/services/structured-output.schema.ts` | Schema Zod — sem alteração (estava correto) |
| `src/services/response-validator.v1.ts` | Original gerado pelo Copilot (preservado) |
| `src/services/response-validator.v2.ts` | Após correções 1–4 do code review |
| `src/services/response-validator.ts` | Versão final — inclui também a cobertura de retorno/reenvio |
| `tests/unit/services/response-validator.test.ts` | Atualizado para o novo nome de export (`safeFallbackResponse`) |

## Versão final para correção

### Arquivos definitivos considerados na correção

- `novatech-assistant/src/services/structured-output.schema.ts`
- `novatech-assistant/src/services/response-validator.ts`
- `novatech-assistant/tests/unit/services/response-validator.test.ts`

### O que foi efetivamente avaliado

- Validade e rigidez do schema Zod (`answer`, `source_document`, `confidence_score`, com `.strict()`).
- Bloqueio determinístico dos 2 guardrails exigidos no exercício, com fallback seguro em falhas.
- Qualidade da revisão crítica (problemas reais identificados, correções aplicadas e regressão revalidada por testes/build).
- Clareza na distinção entre instrução probabilística (prompt) e enforcement determinístico (schema + código).

### Ferramenta usada nas interações deste arquivo

- Todas as interações documentadas neste arquivo foram conduzidas com Claude.

---

## Governança do projeto: guardrails do cenário 2 e AGENTS.md

### Conexão com os guardrails do cenário 2

O `response-validator.ts` implementa dois dos guardrails formalizados pelo Product Specialist no cenário 2 como regras DEVE / NÃO DEVE. A tabela abaixo mapeia cada regra de produto à sua implementação determinística no código:

| Guardrail de produto (cenário 2) | Implementação no código | Camada |
|---|---|---|
| *"Toda resposta DEVE citar a fonte do documento"* | Schema Zod: `source_document: z.string().trim().min(1)` — rejeita se ausente ou vazio | Schema (estrutural) |
| *"Respostas sobre carga perigosa + devolução DEVEM conter negativa explícita"* | `checkDangerousCargoReturnGuardrail()` — regex determinístico aplicado ao `answer` normalizado | Guardrail de conteúdo |

A diferença em relação ao cenário 2 é o nível de garantia: lá, as regras eram intenção de produto expressa em linguagem natural. Aqui, elas são **invariantes do sistema** — um `answer` que viole qualquer uma nunca chega ao atendente, independente do que o modelo produziu.

### Conexão com o AGENTS.md

O `AGENTS.md` do projeto estabelece convenções que o `response-validator.ts` deve seguir. As seções relevantes e como o módulo as implementa:

| Regra do AGENTS.md | Como o módulo a atende |
|---|---|
| **TypeScript strict mode** | O módulo compila sem erros com `noImplicitAny` e `strictNullChecks` — todos os tipos são explícitos (`unknown`, `RejectionDetail`, `CargoGuardrailResult`) |
| **Zod para validação de input** | `structuredOutputSchema.safeParse(rawResponse)` é a primeira verificação — nenhum dado não validado avança no fluxo |
| **pino para logging (nunca `console.log`)** | O módulo aceita um `ValidatorLogger` injetável — não faz logging diretamente, delega ao caller, que deve usar `pino` |
| **Nunca logar dados pessoais** | O `RejectionDetail` registra apenas `guardrailId`, `triggeredPatterns` (nomes de padrões lógicos) e `schemaFieldErrors` (caminhos Zod) — nunca o conteúdo do `answer` |

O ponto mais importante para o AGENTS.md é o `ValidatorLogger` injetável: o módulo não assume nenhuma implementação de log. Isso mantém a separação de responsabilidades e garante que o caller — que conhece o contexto de execução (Azure Function, teste, etc.) — controle onde e como as rejeições são registradas.

## Risco residual do guardrail 2

- Variações semânticas avançadas ainda podem escapar do padrão textual, por exemplo respostas que negam por contexto implícito sem usar sinais linguísticos esperados.
- Frases longas com dupla negação ou construção contraditória podem gerar classificação incorreta (bloquear quando não deveria, ou permitir quando deveria bloquear).
- Termos de domínio novos (sinônimos não catalogados pela operação da NovaTech) podem surgir em produção e exigir atualização periódica dos padrões e dos testes.

---

## Síntese: prompt (probabilístico) vs código (determinístico)

O exercício ilustra a distinção central do harness de governança:

| Camada | Mecanismo | Garantia |
|---|---|---|
| **System prompt** | Instrui o modelo a responder em JSON com `answer`, `source_document`, `confidence_score` | Probabilística — o modelo geralmente obedece, mas pode "esquecer" |
| **Schema Zod** | Valida estrutura e tipos antes de qualquer lógica de negócio | Determinística — se o campo não existe ou está vazio, a resposta é rejeitada sempre |
| **Guardrails de código** | Verificam semântica do conteúdo (ex: carga perigosa + devolução sem negativa) | Determinística — regex aplicado ao texto normalizado, resultado sempre previsível |

O prompt reduz a frequência de respostas mal formadas; o código elimina o risco residual. São complementares, não redundantes.
