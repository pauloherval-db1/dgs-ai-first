# Log de Conversa — Análise Técnica RAG Novatech

| | |
|---|---|
| **Data** | 28/05/2026 |
| **Participante** | Paulo Herval |
| **Assistente** | Claude Sonnet 4.6 (Claude Code) |
| **Contexto** | Exercício Fase 1 — Entendimento do pipeline de RAG para assistente de IA da Novatech |

---

## Turno 1

**Pergunta:**
Quais os desafios para o pipeline de RAG, como isso afeta a qualidade das respostas, e quais estratégias de tratamento?

**Resposta — síntese:**
Análise completa em três eixos:

- **Desafios de ingestão:** PDFs com tabelas complexas (destruição da estrutura linha×coluna), PDFs escaneados (ruído OCR, imagens invisíveis), Confluence com macros e links internos, planilhas com fórmulas sem semântica.
- **Contradições na base:** PROC-042 v1 e v2 coexistem sem marcação de obsolescência; FAQ informal tratado com mesmo peso que documentos normativos.
- **Efeito lost in the middle:** chunks relevantes no meio de contextos longos têm atenção degradada pelo modelo.
- **Estratégias:** parsing por tipo de fonte, chunking semântico, metadata enriquecido, retrieval com filtro de autoridade, posicionamento estratégico no contexto, instrução explícita sobre conflitos.

---

## Turno 2

**Pergunta:**
Organize as respostas para cada tipo de fonte existente: PDFs com tabelas, PDFs escaneados, wiki com links, planilhas com fórmulas.

**Resposta — síntese:**

### PDFs com tabelas
- **Desafio:** serialização linear destrói estrutura; chunks parciais são ininterpretáveis.
- **Impacto:** SLA e frete calculados incorretamente.
- **Estratégia:** `pdfplumber`/`camelot`, serialização como JSON, chunk atômico por tabela.

### PDFs escaneados
- **Desafio:** ruído OCR em valores numéricos; fluxogramas invisíveis ao pipeline.
- **Impacto:** valores corrompidos apresentados com confiança; conteúdo visual ausente.
- **Estratégia:** OCR com score de confiança por bloco, extração visual via modelo multimodal, dicionário de domínio para pós-processamento.

### Wiki Confluence com links internos
- **Desafio:** dependências implícitas entre páginas; macros geram lixo textual; versões antigas indexáveis.
- **Impacto:** resposta incompleta por falta do documento referenciado.
- **Estratégia:** API REST do Confluence, pré-processamento de macros por tipo, grafo de dependências com expansão automática, filtro por `version.when`.

### Planilhas com fórmulas interdependentes
- **Desafio:** fórmulas sem semântica; dependências externas não resolvidas; dados com TTL mensal.
- **Impacto:** valores desatualizados ou ausentes; lógica condicional perdida.
- **Estratégia:** extração de valores resolvidos (`openpyxl`/`xlwings`), documentação da lógica em linguagem natural, TTL explícito no metadata, ingestão incremental por hash de conteúdo.

---

## Turno 3

**Pergunta:**
Estimativa do tamanho aproximado da base em tokens considerando ~800 PDFs (10 páginas cada), ~400 páginas wiki (1.500 palavras cada) e ~50 planilhas. Regra: ~0,75 palavras por token.

**Resposta — síntese:**

| Fonte | Palavras | Tokens |
|---|---|---|
| PDFs (800 × 10 pág × 250 palavras/pág) | 2.000.000 | ~2.667.000 |
| Wiki (400 × 1.500 palavras) | 600.000 | ~800.000 |
| Planilhas (50 × 1.500 palavras) | 75.000 | ~100.000 |
| **Total bruto** | **2.675.000** | **~3.567.000** |
| **Total com overhead (+20%)** | — | **~4.280.000** |

**Implicações:**
- Base é 18× maior que a janela do GPT-4o → RAG obrigatório.
- ~7.000 chunks de 512 tokens → ~42MB de embeddings → escala modesta, gerenciável.
- Gargalo é qualidade do retrieval, não infraestrutura.

---

## Turno 4

**Pergunta:**
GPT-4o tem 128K tokens de janela e system prompt consome ~2K. Quantos chunks de ~500 tokens cabem por query? Como isso afeta a estratégia de chunking e retrieval?

**Resposta — síntese:**

```
128.000 - 2.000 (system) - 200 (pergunta) - 2.000 (resposta) - 10.000 (histórico)
= 113.800 tokens disponíveis para chunks
113.800 / 500 = ~227 chunks (teto teórico)
```

**O paradoxo:** ter capacidade para 227 chunks não significa usá-los todos. O efeito *lost in the middle* degrada atenção do modelo para conteúdo nas posições intermediárias. Zona confiável: primeiros e últimos ~10–15 chunks.

**Implicações para chunking e retrieval:**
- Meta: 8–15 chunks de alta precisão, não o teto de 227.
- Pipeline em dois estágios: busca vetorial ampla (top 50–100) → reranking (top 8–12).
- Conflitos de versão resolvidos por metadata antes do contexto.
- Chunk mais relevante posicionado na posição 1 do contexto.

---

## Turno 5

**Pergunta:**
Recomendação de estratégia de chunking justificada pelo tipo de pergunta e pelo conceito de *lost in the middle*.

**Resposta — síntese:**

Tipos de pergunta identificados no contexto da Novatech:

| Tipo | Exemplo | Necessidade do chunk |
|---|---|---|
| Lookup pontual | "Qual o SLA Gold?" | Valor + contexto mínimo |
| Cálculo | "Frete de 2.000kg para Nordeste?" | Fórmula + tabelas juntas |
| Processo sequencial | "Como abrir devolução?" | Todos os passos |
| Regra + exceção | "Posso devolver carga perigosa?" | Regra e exceção no mesmo chunk |

**Regras de chunking por padrão de conteúdo:**

| Conteúdo | Regra |
|---|---|
| Texto corrido | 500 tokens + overlap de ~75 tokens |
| Tabelas | Chunk atômico (nunca partir) |
| Regra + exceções | Sempre no mesmo chunk |
| Procedimento sequencial | Lista completa no mesmo chunk |
| Fórmula de cálculo | Fórmula + todas as tabelas de parâmetros |

**Metadado obrigatório no prefixo de cada chunk:** `doc_id`, `versão`, `vigência`, `tipo`.

**Conexão com lost in the middle:** chunking semântico reduz o número de chunks necessários por query de 3–4 para 1, posicionando a informação crítica no início do contexto — zona de alta atenção do modelo.

---

## Turno 6

**Entregável solicitado:**
Análise técnica de 1–2 páginas em formato markdown, pronta para entrega.

**Arquivo gerado:** [`analise-tecnica.md`](./analise-tecnica.md)

Documento consolidado com: contexto, desafios por tipo de fonte, impacto na qualidade, capacidade de contexto e *lost in the middle*, estratégia de chunking recomendada, e viabilidade técnica com pré-condições bloqueantes.

---

## Pré-condições bloqueantes identificadas

Independentemente da qualidade técnica do pipeline, três condições são necessárias antes do go-live:

1. **Resolver conflito PROC-042** — marcar v1 como obsoleta no SharePoint e no índice.
2. **Classificar autoridade dos documentos** — FAQ informal não deve competir com normativas no retrieval.
3. **Documentar os gaps** — carga danificada, seguro de carga e frete padrão (<500kg) não têm cobertura formal; o assistente deve ser instruído a não responder e encaminhar ao responsável.

---

## Turno 7

**Pergunta:**
Gere uma v2 do arquivo adicionando `v2` ao final do filename e inclua uma tabela com histórico e modificações feitas.

**Resposta — síntese:**
Arquivo gerado: [`cenario-1-avaliacao-desenvolvedor-v2.md`](./cenario-1-avaliacao-desenvolvedor-v2.md)

Adições em relação à v1:
- Tabela de histórico de revisões no topo do documento.
- Seção 5 — Seleção do Modelo de Embedding: tabela comparativa (`text-embedding-3-large`, `multilingual-e5-large`, `e5-mistral-7b-instruct`, fine-tuning) com recomendação justificada.
- Pipeline de retrieval expandido de 2 para 3 estágios: Recall (busca híbrida dense + BM25 + RRF) → Filtro de metadata → Precision (cross-encoder).
- Estratégia de resolução de links Confluence por grafo (`parent_doc_id`, `linked_doc_ids`).
- Serialização de fórmulas: `formula` + `computed_value` + `snapshot_date` no ingest.
- Threshold OCR: blocos com confiança < 85% sinalizados e excluídos de queries numéricas.
- Seção 7 — Guardrails: classificador de intent pré-retrieval + verificação pós-retrieval por threshold de similaridade (0,75).
- Seção 8 — Latência e Caching: tabela de estimativas por etapa, cache semântico com Redis, reranker INT8.
- Seção 9 — Framework de Avaliação: métricas RAGAS (Context Recall, Context Precision, Faithfulness, Answer Relevancy) com metas mínimas.
- Pré-condições bloqueantes expandidas de 3 para 4 (adicionado golden set de avaliação).
- Correção de posicionamento de chunks: início **e** fim do contexto, não apenas primeira posição.

---

## Turno 8

**Pergunta:**
O cálculo que diz que a base é 18 vezes maior está correto?

**Resposta — síntese:**
Não. O cálculo está errado.

```
3.600.000 tokens (base) / 128.000 tokens (GPT-4o) = 28,1×
```

O multiplicador correto é **~28×**, não 18×. O valor 18 provavelmente originou-se de erro aritmético na sessão anterior (possivelmente usando 200K como denominador, onde 18 × 200.000 = 3.600.000). O documento original propagou esse erro sem revisão.

---

## Turno 9

**Pergunta:**
Faça a correção e crie uma v3 do arquivo. Também atualize o `conversa-log.md` com os prompts e respostas dessa sessão, seguindo o padrão existente.

**Resposta — síntese:**
Arquivo gerado: [`cenario-1-avaliacao-desenvolvedor-v3.md`](./cenario-1-avaliacao-desenvolvedor-v3.md)

Alterações em relação à v2:
- Tabela de histórico atualizada com entrada v3.
- Seção 1: multiplicador corrigido de `18 vezes` para `~28 vezes` com cálculo inline explícito (`3.600.000 / 128.000 = 28,1`).
- Rodapé do documento atualizado mencionando a correção da v3.

`conversa-log.md` atualizado com Turnos 7 a 9 desta sessão.

---

*Log gerado automaticamente ao final da sessão de análise.*
