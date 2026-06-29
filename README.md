# DGS AI First - DB1

Repositório para armazenar os arquivos desenvolvidos durante a execução da trilha de certificação AI First da DB1.

---

## 📚 Cenários de Aprendizado

### ✅ Cenário 1 — Entendimento e Contexto

**Tópicos cobertos:**
- Fundamentos de IA Generativa
- Engenharia de Prompt
- Engenharia de Contexto
- RAG e MCP

**Exercícios:** Ex 1.1 (Análise de Viabilidade), Ex 1.2 (Engenharia de Prompts), Ex 1.3 (Implementação RAG)

**Localização:** `/entregaveis/ex1-1/`, `/entregaveis/ex1-2/`, `/entregaveis/ex1-3/`

**Status:** ✅ Concluído

#### 📋 Contexto do Projeto
A NovaTech enfrenta gargalo operacional — equipes de atendimento gastam ~12 minutos por chamado buscando informações em ~800 documentos (SharePoint), ~400 páginas (Confluence) e planilhas. **Objetivo:** Reduzir esse tempo para menos de 2 minutos via assistente de IA que responda perguntas em linguagem natural com rastreabilidade documental.

#### 📦 O que foi desenvolvido

**Documentação Base (Anexos):**
- Anexo A: Documentação simulada da NovaTech (5 documentos-chave: POL-001, PROC-042 v1 e v2, SLA-2024, FAQ-Atendimento)
- Anexo B: Chunks de referência do pipeline RAG com mapa de cobertura

**Ex 1.1 — Análise de Viabilidade:**
- Análise de riscos e impacto técnico da solução RAG
- Proposta de arquitetura com justificativas

**Ex 1.2 — Engenharia de Prompts (Iterações v1 → v3):**
- Desenvolvimento iterativo do system prompt do assistente
- Regras de priorização de fontes (documentos normativos vs. informais)
- Tratamento de conflitos entre versões PROC-042 v1/v2
- Regras obrigatórias para rastreabilidade e segurança

**Ex 1.3 — Implementação da Pipeline RAG (Python):**
- Stack: Python + ChromaDB + Sentence Transformers + LangChain
- Componentes: chunking, embedding, ingestão, retrieval, prompt_builder, orquestração
- Testes de validação com 5 cenários

#### 🎯 Principais Decisões Técnicas
| Decisão | Justificativa |
|---------|-------------|
| Chunking Híbrido | Preserva coerência semântica com controle de tamanho |
| Dupla indexação (PROC-042 v1 + v2) | Mantém histórico e permite rastreamentos temporais |
| Reordenação por prioridade | Impede que FAQ informal sobrepuje documentos oficiais |
| ChromaDB local | PoC ágil, escalável para Azure Cognitive Search |
| Metadados enriquecidos | doc_id, versão, vigência, autoridade |

#### ⚠️ Desafios Identificados
1. Conflito de versões: PROC-042 v1 e v2 coexistem sem marcação de obsolescência
2. Tabelas partidas: Parsers genéricos destroem relacionamento linha×coluna
3. "Lost in the Middle": Chunks relevantes no meio do contexto = menor atenção do modelo
4. OCR em PDFs escaneados: Ruído em valores críticos
5. Links Confluence não resolvidos: Páginas referenciadas não são trazidas automaticamente

#### 🧪 Testes e Resultados
Validação da pipeline com 5 cenários de teste com resultados em `entregaveis/ex1-3/outputs/testes/` demonstrando retrieval e prompts esperados.

#### 🔑 Conhecimentos Consolidados
- Fundamentos de IA Generativa e RAG
- Engenharia de Prompts (system prompt, chain-of-thought, safety rules)
- Engenharia de Contexto (chunking, embedding, retrieval)
- Governança documental e resolução de conflitos em bases híbridas
- Implementação MLOps com Python + vector stores

---

### 🔄 Cenário 2 — [Nome a Definir]

**Tópicos cobertos:**
- [A definir]

**Exercícios:** Ex 2.1, Ex 2.2, Ex 2.3

**Localização:** `/entregaveis/ex2-1/`, `/entregaveis/ex2-2/`, `/entregaveis/ex2-3/`

**Status:** ⏳ Planejado

#### 📋 Contexto do Projeto
[A definir]

#### 📦 O que foi desenvolvido
[A definir]

#### 🎯 Principais Decisões Técnicas
[A definir]

#### ⚠️ Desafios Identificados
[A definir]

#### 🧪 Testes e Resultados
[A definir]

#### 🔑 Conhecimentos Consolidados
[A definir]

---

### 🚧 Cenário 3 — Governança e Qualidade de Respostas

**Tópicos cobertos:**
- Harness Engineering
- Structured Output com Zod
- Guardrails determinísticos
- Code Review orientado a riscos

**Exercícios:** Ex 3.1, Ex 3.2, Ex 3.3

**Localização:** `/entregaveis/ex3-1/`, `/entregaveis/ex3-2/`, `/entregaveis/ex3-3/`

**Status:** 🔄 Em andamento (Ex 3.1 concluído)

#### 📋 Contexto do Projeto
No Ex 3.1, o foco foi fortalecer a confiabilidade das respostas do assistente NovaTech por meio de validação determinística no pós-processamento da saída do modelo. O objetivo foi reduzir risco operacional quando o modelo produzir respostas fora do formato esperado ou sem as negativas obrigatórias para cenários críticos.

#### 📦 O que foi desenvolvido (Ex 3.1)
- Definição de `structured output` com schema Zod estrito para os campos `answer`, `source_document` e `confidence_score`.
- Implementação de validador de respostas com fallback seguro em caso de rejeição.
- Aplicação de guardrails determinísticos:
	- Guardrail 1: rejeitar respostas que não passem na validação de schema (inclui ausência/invalidez de `source_document`).
	- Guardrail 2: bloquear respostas que mencionam carga perigosa + devolução sem sinal negativo explícito.
- Registro estruturado de motivo de rejeição (`RejectionReason`) e metadados (`RejectionDetail`) para rastreabilidade.
- Expansão de regex para cobrir sinônimos logísticos e sinais negativos adicionais (redução de falso negativo).
- Refatoração para separar contrato (`structured-output.schema.ts`) da regra de negócio (`response-validator.ts`).
- Geração de artefatos de evidência da sessão:
	- Export completo de prompts e respostas
	- Sessão de code review com problemas identificados e correções aplicadas

#### 🎯 Principais Decisões Técnicas
| Decisão | Justificativa |
|---------|---------------|
| `structuredOutputSchema` com `.strict()` | Rejeita campos extras e força contrato de saída controlado |
| Fallback seguro padronizado | Evita resposta potencialmente insegura em caso de falha |
| Guardrail por código (determinístico) além do prompt | Prompt é probabilístico; regra crítica precisa ser enforcement obrigatório |
| Separação schema x validator | Melhora manutenção, testabilidade e clareza arquitetural |
| Enriquecimento de motivos de rejeição | Aumenta observabilidade e suporte a auditoria |

#### ⚠️ Desafios Identificados
1. Dead code inicial no guardrail de `source_document` devido à validação já coberta no schema.
2. Cobertura limitada de regex no primeiro draft para detecção de carga perigosa e devolução.
3. Necessidade de explicitar no código a distinção entre controle probabilístico (prompt) e controle determinístico (guardrails).

#### 🧪 Testes e Resultados
- Testes unitários do validador executados com sucesso para cenários de aceite/rejeição.
- Build TypeScript validado sem regressões nos módulos alterados.
- Critérios esperados do Ex 3.1 atendidos:
	- Saída estruturada validável
	- Rejeição determinística de respostas fora de política
	- Fallback seguro consistente

#### 📁 Evidências e Entregáveis do Ex 3.1
- `entregaveis/ex3-1/sessao-code-review.md`
- `entregaveis/ex3-1/export-sessao-prompts-respostas.md`
- `entregaveis/ex3-1/response-validator.ts`
- `entregaveis/ex3-1/structured-output.schema.ts`

#### 🔑 Conhecimentos Consolidados
- Como transformar requisitos de segurança em guardrails determinísticos auditáveis.
- Como usar Zod para enforce de contrato de saída em aplicações LLM.
- Como conduzir code review focado em risco real (dead code, cobertura insuficiente e clareza de responsabilidade).
