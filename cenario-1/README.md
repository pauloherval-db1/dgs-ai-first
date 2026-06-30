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
