# Exercício 3.2 — Revisão crítica de código gerado por IA
**Papel:** Desenvolvedor (revisão feita por Claude — claude-sonnet-4-6)  
**Tópico:** Revisão Crítica de Outputs de IA  
**Data:** 2026-06-29

> Esta revisão foi gerada por Claude Code (claude-sonnet-4-6) após leitura do módulo `feedback-handler.ts` gerado pelo Copilot, do `AGENTS.md` do projeto, da estrutura de arquivos em `/src`, do `package.json` e dos padrões estabelecidos em `query/validator.ts` e `query/handler.ts` como referência de como o projeto espera que handlers sejam escritos.

---

## Problemas encontrados

### 1 — Arquivo no lugar errado

O Copilot gerou o arquivo como `feedback-handler.ts` na raiz. A estrutura do projeto segue o padrão `/src/functions/<domínio>/handler.ts`, já estabelecido por `query/handler.ts` e `health/handler.ts`. O arquivo correto é `/src/functions/feedback/handler.ts`.

**Tipo:** desvio estrutural  
**Bloqueia merge?** Não diretamente, mas gera confusão de localização e quebra a convenção do projeto.

---

### 2 — Sem validação de input (`as any` + ausência de Zod)

```typescript
const body = await request.json() as any;
```

O cast `as any` anula a type safety do TypeScript inteiramente. Qualquer payload é aceito sem verificação. O padrão do projeto (ver `query/validator.ts`) é declarar um schema Zod, chamá-lo com `.parse()` e rejeitar inputs inválidos com mensagem estruturada antes de qualquer lógica de negócio.

**Tipo:** violação do AGENTS.md, bug de segurança  
**Bloqueia merge?** Sim.

---

### 3 — Vazamento de PII via log

```typescript
console.log('Feedback recebido:', JSON.stringify(feedback));
```

`attendantEmail` é dado pessoal (PII). Logar o objeto completo serializado expõe o e-mail do atendente em stdout e potencialmente no Application Insights sem controle de acesso ou ofuscação. Dois problemas sobrepostos:

- **Privacidade:** campo sensível não deve aparecer em log de nível INFO.
- **Ferramenta errada:** o stub de `query/handler.ts` documenta explicitamente `"sem console.log"` — o projeto usa `pino`, que permite logging estruturado com níveis configuráveis e redação de campos sensíveis.

**Tipo:** falha de segurança, violação do AGENTS.md  
**Bloqueia merge?** Sim.

---

### 4 — `require()` dinâmico dentro de função assíncrona — quebra em runtime

```typescript
const { CosmosClient } = require('@azure/cosmos');
const client = new CosmosClient(process.env.COSMOS_CONNECTION_STRING);
```

`package.json` declara `"type": "module"`. Em projetos ESM, `require` não está disponível — isso lança `ReferenceError: require is not defined` em runtime, não em tempo de compilação. O import deve ser estático no topo do arquivo:

```typescript
import { CosmosClient } from '@azure/cosmos';
```

Problema adicional: mesmo corrigindo o import, instanciar `CosmosClient` dentro do handler cria uma nova conexão TCP a cada requisição. O cliente deve ser instanciado uma única vez no escopo do módulo.

**Tipo:** erro de runtime, ineficiência  
**Bloqueia merge?** Sim (o `require` quebra o processo).

---

### 5 — Sem tratamento de erro

Se `container.items.create(feedback)` lança (Cosmos indisponível, quota excedida, documento duplicado), a função crasha com HTTP 500 sem corpo e sem log estruturado. O contrato da API deveria retornar `400` para input inválido e `500` com mensagem padronizada para falhas de infraestrutura.

**Tipo:** bug potencial  
**Bloqueia merge?** Sim.

---

## Sumário

| # | Problema | Tipo | Bloqueia merge? |
|---|---|---|---|
| 1 | Arquivo no lugar errado | Estrutural | Não |
| 2 | `as any` + ausência de Zod | AGENTS.md, segurança | **Sim** |
| 3 | Log de PII + `console.log` | Segurança, AGENTS.md | **Sim** |
| 4 | `require()` em ESM + cliente por request | Runtime, eficiência | **Sim** |
| 5 | Sem tratamento de erro | Bug potencial | **Sim** |

**Veredito:** não aprovado para merge. Quatro bloqueadores ativos.
