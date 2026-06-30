# Sessão de Revisão Técnica — Análise RAG Novatech

| | |
|---|---|
| **Data** | 28/05/2026 |
| **Revisor** | Claude Sonnet 4.6 (Claude Code) |
| **Documento revisado** | `cenario-1-avaliacao-desenvolvedor.md` (v1) |
| **Documentos gerados** | `cenario-1-avaliacao-desenvolvedor-v2.md`, `v3.md` |

---

## Prompt enviado

> *"Claude, você é um arquiteto de software especializado em agentes LLM e RAG, avalie o documento a seguir e dê seu parecer."*

---

## Output recebido

### Pontos fortes confirmados

1. **Diagnóstico de fontes heterogêneas** — A identificação de que tabelas partidas entre chunks perdem valor semântico, que OCR não propaga confiança por bloco e que macros Confluence geram lixo são problemas reais e frequentemente ignorados em projetos RAG iniciantes.

2. **Pipeline em dois estágios (recall + reranking)** — Busca vetorial ampla + cross-encoder é a arquitetura certa para o volume. Top-50 → reranker → top-8 é um range razoável.

3. **Resolução de conflitos na camada de metadata** — Delegar a arbitragem de versões ao LLM é um anti-pattern perigoso. Filtrar `vigência` antes de montar o contexto é a abordagem correta.

4. **Meta operacional "5–10 chunks de alta precisão"** — Alinhado com a literatura sobre *lost in the middle*.

---

### Lacunas técnicas identificadas

| # | Lacuna | Descrição resumida | Incorporado em |
|---|--------|--------------------|----------------|
| L1 | Modelo de embedding não especificado | Para base em PT-BR com terminologia de logística, a escolha do modelo é decisão crítica. `multilingual-e5-large` recomendado para início. | v2 — Seção 5 |
| L2 | Busca híbrida ausente | Apenas dense retrieval. BM25/sparse é superior para queries com termos exatos (`"PROC-042"`, valores numéricos). Fusão via RRF não mencionada. | v2 — Seção 6 |
| L3 | Fórmulas de planilhas sem solução | Problema diagnosticado, mas pipeline não propõe serialização de `formula` + `computed_value` + `snapshot_date` no ingest. | v2 — Seção 2 |
| L4 | Confluence: links internos sem estratégia | Problema identificado, mas crawl por grafo com `parent_doc_id` e `linked_doc_ids` ausente. | v2 — Seção 2 |
| L5 | Framework de avaliação ausente | Sem RAGAS/TruLens, não há como validar se ajustes de chunking e reranking estão melhorando o pipeline. Go-live sem métricas é inviável. | v2 — Seção 9 |
| L6 | Guardrails apenas no system prompt | Para gaps documentais, instrução no prompt não é mecanismo suficiente. Requer classificador de intent pré-retrieval + threshold pós-retrieval. | v2 — Seção 7 |
| L7 | Latência não endereçada | Pipeline em dois estágios adiciona ~200–400ms de cross-encoder. Sem análise de budget de latência nem caching de queries frequentes. | v2 — Seção 8 |

---

### Inconsistências identificadas

| # | Ponto | Problema | Correção aplicada |
|---|-------|----------|-------------------|
| I1 | Posicionamento de chunks no contexto | Documento recomendava apenas a primeira posição. Atenção do modelo é alta no início **e** no fim — material crítico deve ocupar ambas as extremidades. | v2 — Seção 4 |
| E1 | Multiplicador base vs. janela de contexto | "18 vezes maior" era erro aritmético. Correto: ~28× (3.600.000 / 128.000 = 28,1). | v3 — Seção 1 |

---

*Documento gerado para rastreabilidade do processo de revisão técnica.*
