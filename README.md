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

### 🔄 Cenário 2 — Estruturação do Trabalho

**Tópicos cobertos:**
- Configuração de MCP Servers locais e gratuitos (Ex 2.1)
- Mapeamento de necessidades do projeto para servers MCP (Ex 2.1)
- Aplicação de least privilege por escopo e permissões (Ex 2.1)
- Desenvolvimento de query endpoint com TypeScript + Zod (Ex 2.2)
- Iteração código-testes com validação de build (Ex 2.2)
- Revisão crítica de artefatos e identificação de melhorias (Ex 2.2)

**Exercícios:** Ex 2.1 (✅ concluído), Ex 2.2 (✅ concluído), Ex 2.3 (✅ concluído)

**Localização:** `/entregaveis/ex2-1/`, `/entregaveis/ex2-2/`

**Status:** ✅ Concluído

#### 📋 Contexto do Projeto
Na fase de estruturação, o foco foi: (1) preparar o ambiente para trabalho AI First com acesso controlado a código, documentação de negócio e corpus via MCP sem serviços externos; (2) implementar tarefas concretas de desenvolvimento do query endpoint com validação e iteração.

#### 📦 O que foi desenvolvido

**Ex 2.1 — MCP Servers:**
- `mcp.json` com servers `filesystem-rw`, `filesystem-ro-docs`, `filesystem-ro-prompts`, `git`, `memory` e `everything`
- Documento de mapeamento (`mapeamento-mcp-servers.md`) relacionando necessidade × server × escopo
- Export da sessão (`session-export.md`) com prompts e respostas estruturados
- Evidências visuais em capturas de tela

**Ex 2.2 — Query Endpoint (desenvolvimento):**
- `src/shared/types.ts` — tipos de domínio (`QueryRequest`, `QueryResponse`, `SearchChunk`, `SourceDocument`)
- `src/shared/messages.ts` — centralização de mensagens de erro (refatoração iterativa)
- `src/functions/query/validator.ts` — validação com Zod de requisições POST
- `tests/unit/query/validator.test.ts` — 4 cenários de teste (campo ausente, vazio, limite, válido)
- Compilação e testes executados com sucesso (`npm run build`, `npm test`)
- Refactoring: substituição de strings por `ZodIssueCode` (Turno 3) e extração de mensagens (Turno 5)

**Ex 2.3 — Skills Foundation (governança de skills):**
- `SKILL.md` — skill Foundation com contexto, regras prescritivas, exemplos concretos DO/DON'T e anti-padrões úteis
- Ajuste iterativo da skill para reforçar `camelCase` em variáveis, funções e objetos em TypeScript
- Revisão da regra assíncrona para equilibrar `async/await` e `then`, evitando uso excessivo de `await`
- Reforço explícito para evitar erros genéricos e preferir `try/catch` e erros específicos quando possível
- `mapeamento-skills.md` — mapeamento determinístico de triggers, skills obrigatórias, papéis e frequência de uso
- `arvore-de-skills.md` — organização hierárquica das skills por camada e dependência
- `session-export.md` — export da sessão com prompts, respostas e referência explícita ao uso do GitHub Copilot na criação da skill

#### 🎯 Principais Decisões Técnicas
| Decisão | Justificativa |
|---------|-------------|
| Separar `filesystem-rw` e `filesystem-ro-*` | Reduz risco de escrita acidental em documentação/prompt |
| TypeScript strict + Zod para validação | Type safety e validação em tempo de execução |
| Schema centralizado em `types.ts` | Reduz duplicação de regra de validação (`question` em um único lugar) |
| Mensagens em map centralizado | Facilita manutenção e i18n futuro |
| Testes unitários sem mocks de rede | Foco em comportamento local, isolado de dependências |
| Skills prescritivas e machine-readable | Permitem que agentes sigam regras sem ambiguidade |
| Regras de estilo e erros explícitas | Reduzem geração de código frágil ou genérico |

#### ⚠️ Desafios Identificados
1. **Ex 2.1:** Servidores de filesystem expõem tools de escrita por padrão, exigindo mitigação por escopo e permissões
2. **Ex 2.2:** Duplicação de regra de validação entre schema de domínio e validador do endpoint (problema 1 da revisão crítica)
3. **Ex 2.2:** Error handling genérico dificulta integração com handler HTTP (problema 2 da revisão crítica)
4. **Ex 2.2:** Cobertura de testes não inclui `session_id` inválido nem múltiplos erros simultâneos (problema 3 da revisão crítica)
5. **Ex 2.3:** Skills narrativas ou ambíguas precisam ser reescritas como instruções prescritivas para consumo por agentes

#### 🧪 Testes e Resultados

**Ex 2.1:**
- Validação em `entregaveis/ex2-1/session-export.md`: leitura de doc, recuperação de chunk, consulta git

**Ex 2.2:**
- Execução de `npm test -- tests/unit/query/validator.test.ts` com **4/4 testes passando**
- Execução de `npm run build` com **0 erros de compilação**
- Iteração validada: Turno 3 (ZodIssueCode) e Turno 5 (messages.ts)
- Revisão crítica: 3 problemas reais identificados e documentados em `entregaveis/ex2-2/revisao-participante-ex2-2.md`

**Ex 2.3:**
- `entregaveis/ex2-3/SKILL.md` criado e depois refinado com melhorias prescritivas solicitadas pelo usuário
- `entregaveis/ex2-3/mapeamento-skills.md` documenta triggers e uso determinístico das skills no projeto
- `entregaveis/ex2-3/arvore-de-skills.md` organiza a estrutura de skills Foundation/Domain/Artifact
- `entregaveis/ex2-3/session-export.md` consolida a sessão e registra a criação da skill com suporte do Copilot
- A skill final prioriza regras executáveis, exemplos reais e anti-padrões acionáveis

#### 🔑 Conhecimentos Consolidados
- Design de integração MCP para desenvolvimento AI First
- Princípios de segurança (least privilege) em contexto de agentes
- Desenvolvimento iterativo dirigido por testes em TypeScript
- Identificação de problemas reais em código gerado (duplicação, error handling, cobertura)
- Estruturação de entregáveis com rastreabilidade de critérios e ADRs
- Escrita de skills prescritivas para agentes de IA
- Organização de governança por triggers, dependências e frequência de uso
- Refinamento de instruções para reduzir ambiguidade na geração assistida

---

### 🔄 Cenário 3 — [Nome a Definir]

**Tópicos cobertos:**
- [A definir]

**Exercícios:** Ex 3.1, Ex 3.2, Ex 3.3

**Localização:** `/entregaveis/ex3-1/`, `/entregaveis/ex3-2/`, `/entregaveis/ex3-3/`

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
