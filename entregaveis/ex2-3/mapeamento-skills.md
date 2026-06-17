# Mapeamento de Skills — NovaTech Assistant

> Para cada skill: nome, frase-ativação, quem cria, quem consome (papel + agente), e frequência estimada de uso.

## Regras determinísticas de execução por agente

As regras abaixo são mandatórias para reduzir ambiguidade e tornar o consumo das skills machine-readable.

| Trigger detectado no prompt | Skill obrigatória | Ação mandatória do agente |
|---|---|---|
| Pedido de geração TypeScript (`.ts`, endpoint, service, teste) | `typescript-conventions` | Ler e aplicar antes de sugerir qualquer linha de código. Se houver conflito com outra skill, esta skill prevalece para estilo e tipagem. |
| Pedido com erro/exception/status code/retry | `error-handling` | Aplicar taxonomia de erros do projeto e proibir `throw new Error()` genérico em handlers e services. |
| Pedido de criação/movimento de arquivo/módulo | `project-structure` | Resolver path alvo antes de gerar código; bloquear geração se o destino não existir na estrutura aprovada. |
| Pedido de HTTP trigger/rota API | `azure-functions-endpoint` | Gerar contrato de 3 arquivos (`handler`, `validator`, `response-builder`) e validar fronteira handler/service. |
| Pedido de retrieval/chunks/busca semântica | `azure-ai-search-integration` | Usar `SearchService` tipado e retornar `SearchChunk[]`; não expor tipos nativos do SDK. |
| Pedido de React card/UI Teams | `react-components` | Selecionar template React ou Adaptive Card e incluir campos de fonte/feedback exigidos pelo domínio. |
| Pedido de testes unitários/integração | `testing-patterns` | Definir categoria (`unit`/`integration`/`e2e`) antes de escrever testes e usar fixtures oficiais. |
| Pedido de novo endpoint RAG completo | `create-rag-endpoint` | Executar checklist da artifact skill e carregar pré-requisitos na ordem definida. |
| Pedido de teste de integração de endpoint | `create-integration-test` | Executar checklist da artifact skill e cobrir, no mínimo, happy path + erros mandatórios. |

---

## Foundation

### 1. `typescript-conventions`

| Campo | Valor |
|---|---|
| **Nome** | TypeScript Conventions |
| **Frase-ativação** | "gere código TypeScript" / "crie um arquivo .ts" / "implemente [qualquer coisa] em TypeScript" |
| **Quem cria** | Tech Lead — define as convenções do projeto no início do cenário |
| **Quem consome (papéis)** | Dev Sênior, Dev, QA — todo papel que escreve ou revisa código |
| **Quem consome (agentes)** | Copilot (toda sugestão de código), Claude Code (toda implementação de feature) |
| **Frequência** | **Contínua** — 100% dos arquivos `.ts` gerados. É a skill mais acionada do projeto. |

**Regra mandatória:** toda geração de código deve começar por `typescript-conventions`; sem isso o output é inválido para merge.

---

### 2. `error-handling`

| Campo | Valor |
|---|---|
| **Nome** | Error Handling |
| **Frase-ativação** | "adicione tratamento de erro" / "crie um custom error" / "o endpoint precisa retornar erro adequado" |
| **Quem cria** | Tech Lead — junto com a criação de `src/shared/errors.ts` |
| **Quem consome (papéis)** | Dev Sênior, Dev |
| **Quem consome (agentes)** | Copilot (ao gerar handlers e services), Claude Code (ao implementar qualquer módulo com IO externo) |
| **Frequência** | **Alta** — todo handler, service e pipeline de ingestão. Estimativa: acionada em ~80% das sessões de geração de código. |

**Regra mandatória:** quando houver exceções, o agente deve usar erro tipado do domínio e mapeamento HTTP explícito no handler.

---

### 3. `project-structure`

| Campo | Valor |
|---|---|
| **Nome** | Project Structure |
| **Frase-ativação** | "onde devo criar este arquivo?" / "crie um novo módulo" / "adicione configuração de ambiente" / "configure logging para [módulo]" |
| **Quem cria** | Tech Lead — documenta a estrutura de diretórios e convenções de config/logging |
| **Quem consome (papéis)** | Dev Sênior, Dev, QA (localizar fixtures), Product Specialist (localizar specs) |
| **Quem consome (agentes)** | Copilot (orientação de onde criar novos arquivos), Claude Code (navegação e criação de módulos) |
| **Frequência** | **Alta no início, média depois** — acionada a cada novo módulo e a cada vez que um agente precisa decidir onde colocar algo. Estimativa: todo sprint com entrega de novo módulo. |

---

## Domain

### 4. `azure-functions-endpoint`

| Campo | Valor |
|---|---|
| **Nome** | Azure Functions Endpoint |
| **Frase-ativação** | "crie um endpoint" / "adicione uma Azure Function HTTP trigger" / "implemente a rota de [nome]" |
| **Quem cria** | Tech Lead — após definir o primeiro endpoint como referência |
| **Quem consome (papéis)** | Dev, Dev Sênior |
| **Quem consome (agentes)** | Copilot (scaffold dos 3 arquivos), Claude Code (implementação da lógica de orquestração) |
| **Frequência** | **Média-alta** — um por módulo funcional. O projeto tem 5 módulos (query, feedback, health + variações). Estimativa: 5–8 vezes ao longo do desenvolvimento. |

**Dependência direta da artifact skill:** `create-rag-endpoint` não funciona sem esta skill lida primeiro — ela define o contrato dos 3 arquivos que a artifact receita preenche.

---

### 5. `azure-ai-search-integration`

| Campo | Valor |
|---|---|
| **Nome** | Azure AI Search Integration |
| **Frase-ativação** | "busque documentos relevantes" / "integre com Azure AI Search" / "implemente a camada de retrieval" / "recupere chunks para a pergunta" |
| **Quem cria** | Tech Lead / Dev Sênior — ao implementar `src/services/search.ts` pela primeira vez |
| **Quem consome (papéis)** | Dev, Dev Sênior |
| **Quem consome (agentes)** | Copilot (ao completar `SearchService`), Claude Code (ao implementar o pipeline RAG) |
| **Frequência** | **Baixa-média** — `SearchService` é um módulo único, mas a skill é relida a cada vez que a lógica de retrieval é estendida (novo filtro, ajuste de score, novo índice). Estimativa: 3–5 vezes no projeto. |

---

### 6. `react-components`

| Campo | Valor |
|---|---|
| **Nome** | React Components |
| **Frase-ativação** | "crie um componente React" / "crie um card de resposta" / "implemente o painel web" / "adicione feedback card" / "crie Adaptive Card para o Teams" |
| **Quem cria** | Tech Lead / Dev Frontend — ao criar os primeiros componentes de referência |
| **Quem consome (papéis)** | Dev Frontend |
| **Quem consome (agentes)** | Copilot (sugestão de JSX e Adaptive Card JSON), Claude Code (implementação de novos cards e páginas) |
| **Frequência** | **Média** — o painel web e o bot têm um conjunto fixo de componentes. Estimativa: 5–10 componentes ao longo do projeto (ResponseCard, FeedbackCard, SourceList, histórico de conversas, etc.). |

> Regra de manutenção: `create-react-card` permanece descontinuada; novos padrões de card devem ser adicionados apenas em `react-components` (seção "Geração de cards").

---

### 7. `testing-patterns`

| Campo | Valor |
|---|---|
| **Nome** | Testing Patterns |
| **Frase-ativação** | "escreva testes para" / "adicione testes de integração" / "crie fixtures para" / "teste o endpoint de [nome]" |
| **Quem cria** | QA + Tech Lead — define a estratégia de testes no início do projeto |
| **Quem consome (papéis)** | Dev, Dev Sênior, QA |
| **Quem consome (agentes)** | Copilot (geração de casos de teste), Claude Code (implementação de suítes de integração com MSW) |
| **Frequência** | **Alta** — um conjunto de testes por módulo entregue. Estimativa: acionada em paralelo com todo desenvolvimento de código (1:1 com `create-rag-endpoint`). |

---

## Artifact

### 8. `create-rag-endpoint`

| Campo | Valor |
|---|---|
| **Nome** | Create RAG Endpoint |
| **Frase-ativação** | "crie um endpoint RAG" / "adicione uma nova rota de consulta" / "implemente o endpoint de [nome]" |
| **Quem cria** | Dev Sênior — após Tech Lead estabilizar as skills Domain |
| **Quem consome (papéis)** | Dev (usa como receita para scaffolding), Dev Sênior (valida output gerado) |
| **Quem consome (agentes)** | Copilot (gera os 3 arquivos com base no template), Claude Code (implementa a lógica de cada endpoint) |
| **Frequência** | **Alta para o projeto** — é a receita mais reutilizada. Um endpoint RAG por módulo principal: query, feedback e variações. Estimativa: 5+ vezes. |

**Skills pré-requisito que o agente deve ler antes:**
`typescript-conventions` → `error-handling` → `project-structure` → `azure-functions-endpoint` → `azure-ai-search-integration`

---

### 9. `create-integration-test`

| Campo | Valor |
|---|---|
| **Nome** | Create Integration Test |
| **Frase-ativação** | "crie teste de integração para o endpoint" / "adicione integration test para [nome]" / "teste o fluxo completo do handler de [nome]" |
| **Quem cria** | QA + Dev Sênior — ao criar o primeiro teste de integração como referência |
| **Quem consome (papéis)** | Dev, QA |
| **Quem consome (agentes)** | Copilot (geração dos casos de teste e setup do MSW), Claude Code (implementação da suíte completa com todos os cenários de erro) |
| **Frequência** | **Alta** — proporção 1:1 com `create-rag-endpoint`. Todo endpoint novo gera um teste de integração correspondente. Estimativa: 5+ vezes. |

**Skills pré-requisito que o agente deve ler antes:**
`typescript-conventions` → `testing-patterns` → `azure-functions-endpoint`

---

## Visão consolidada

| Skill | Nível | Cria | Consome (papéis) | Consome (agentes) | Freq. estimada |
|---|---|---|---|---|---|
| `typescript-conventions` | Foundation | Tech Lead | Dev Sênior, Dev, QA | Copilot, Claude Code | Contínua — todo .ts |
| `error-handling` | Foundation | Tech Lead | Dev Sênior, Dev | Copilot, Claude Code | ~80% das sessões |
| `project-structure` | Foundation | Tech Lead | Dev Sênior, Dev, QA, PS | Copilot, Claude Code | Todo novo módulo |
| `azure-functions-endpoint` | Domain | Tech Lead | Dev Sênior, Dev | Copilot, Claude Code | 5–8x no projeto |
| `azure-ai-search-integration` | Domain | Tech Lead / Dev Sênior | Dev Sênior, Dev | Copilot, Claude Code | 3–5x no projeto |
| `react-components` ¹ | Domain | Tech Lead / Dev Frontend | Dev Frontend | Copilot, Claude Code | 5–10x no projeto |
| `testing-patterns` | Domain | QA + Tech Lead | Dev Sênior, Dev, QA | Copilot, Claude Code | 1:1 com cada módulo |
| `create-rag-endpoint` | Artifact | Dev Sênior | Dev, Dev Sênior | Copilot, Claude Code | 5+ vezes |
| `create-integration-test` | Artifact | QA + Dev Sênior | Dev, QA | Copilot, Claude Code | 5+ vezes (1:1 endpoint) |

¹ Inclui checklist e templates de geração de cards (absorveu `create-react-card`).

**Legenda de papéis:** PS = Product Specialist
