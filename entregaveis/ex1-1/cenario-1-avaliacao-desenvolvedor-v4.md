# Análise Técnica — Pipeline de RAG para Assistente de IA Novatech

**Data**: 28/05/2026
**Autor**: Paulo + Claude
**Classificação**: Documento técnico

---

## Histórico de Revisões

| Versão | Data       | Autor          | Descrição das Alterações |
|--------|------------|----------------|--------------------------|
| v1     | 28/05/2026 | Paulo + Claude | Versão inicial: diagnóstico de fontes, desafios por tipo, estratégia de chunking, pipeline em dois estágios e viabilidade técnica |
| v2     | 28/05/2026 | Paulo + Claude | Adição: seleção de modelo de embedding, busca híbrida (dense + sparse + RRF), estratégia para fórmulas de planilhas, resolução de links Confluence por grafo, framework de avaliação (RAGAS), guardrails para gaps documentais, análise de latência e caching, correção da estratégia de posicionamento de chunks no contexto |
| v3     | 28/05/2026 | Paulo + Claude | Correção de erro aritmético na Seção 1: multiplicador da base vs. janela de contexto corrigido de 18× para ~28× (3.600.000 / 128.000 = 28,1) |
| v4     | 28/05/2026 | Paulo + Claude | Adição na Seção 1: detalhamento do cálculo de estimativa de tokens com separação explícita entre dados fornecidos e premissas adotadas |

---

## 1. Contexto

A Novatech busca implantar um assistente de IA baseado em RAG (*Retrieval-Augmented Generation*) para suporte ao time de atendimento. A base de conhecimento é composta por ~800 documentos PDF (média de 10 páginas), ~400 páginas wiki no Confluence e ~50 planilhas, totalizando aproximadamente **3,6 milhões de tokens** (~4,3M com overhead de metadata e serialização estruturada).

Essa escala torna o RAG **obrigatório**: a base é ~28 vezes maior que a janela de contexto do GPT-4o (128K tokens) — 3.600.000 / 128.000 = 28,1 —, inviabilizando qualquer abordagem de ingestão total por query.

### 1.1 Detalhamento da estimativa de tokens

O cálculo foi feito em três blocos usando a regra `tokens = palavras / 0,75`.

**PDFs**

A média de palavras por página não foi fornecida. Foi adotada a premissa de **250 palavras/página**, justificada pelo perfil dos documentos: textos operacionais com tabelas, listas e formatação estruturada, que apresentam densidade menor que texto corrido acadêmico (~350–400 palavras/página).

```
800 documentos × 10 páginas        = 8.000 páginas
8.000 páginas × 250 palavras/pág   = 2.000.000 palavras
2.000.000 / 0,75                   = 2.666.667 tokens
```

**Wiki**

A média de palavras por página foi fornecida diretamente no enunciado.

```
400 páginas × 1.500 palavras/pág   = 600.000 palavras
600.000 / 0,75                     = 800.000 tokens
```

**Planilhas**

A média de palavras por planilha não foi fornecida. Foi adotada a premissa de **1.500 palavras/planilha**, estimando planilhas de complexidade média: ~80 linhas × 15 colunas com headers, rótulos e valores textuais.

```
50 planilhas × 1.500 palavras      = 75.000 palavras
75.000 / 0,75                      = 100.000 tokens
```

**Consolidado**

```
2.666.667 + 800.000 + 100.000      = 3.566.667 tokens  ≈  3,6M tokens
```

**Premissas vs. dados fornecidos**

| Parâmetro | Origem |
|---|---|
| 800 PDFs, 10 páginas/doc | Enunciado |
| 400 páginas wiki, 1.500 palavras/página | Enunciado |
| 50 planilhas | Enunciado |
| Regra 0,75 palavras/token | Enunciado |
| **250 palavras/página (PDF)** | **Premissa adotada** |
| **1.500 palavras/planilha** | **Premissa adotada** |

O resultado é sensível principalmente à premissa de 250 palavras/página para PDFs, que representa 74% do total estimado. Se a média real for 350 palavras/página, o total sobe para ~4,9M tokens. A ordem de grandeza se mantém em ambos os cenários — o que é suficiente para confirmar que o RAG é obrigatório.

---

## 2. Desafios por Tipo de Fonte

### PDFs com tabelas complexas

Parsers genéricos serializam tabelas em texto linear, destruindo o relacionamento linha×coluna. Tabelas partidas entre chunks tornam-se ininterpretáveis — o chunk sem cabeçalho não carrega informação útil. Para a Novatech, isso afeta diretamente os cálculos de frete (PROC-042) e a tabela de SLAs, podendo gerar valores numericamente incorretos com aparência de confiança.

### PDFs escaneados

OCR introduz ruído tipográfico sistemático em valores críticos (`1.O` vs `1.0`, erros em dígitos de multiplicadores e prazos). Fluxogramas embutidos como imagens são completamente ignorados pelo pipeline padrão — o conteúdo visual não entra no índice. A confiança variável por bloco OCR não é propagada ao retriever, que trata texto corrompido com o mesmo peso que texto íntegro.

Blocos com score de confiança OCR abaixo de 85% devem ser sinalizados no metadata do chunk (`ocr_confidence: low`) e excluídos do retrieval para perguntas que envolvam valores numéricos ou prazos, sendo encaminhados para revisão humana.

### Wiki Confluence com links internos

Cada página é ingerida como documento isolado, mas links internos criam dependências implícitas de conteúdo — a página referenciada não é automaticamente trazida ao contexto. Macros customizadas (`{warning}`, `{expand}`, `{info}`) geram lixo textual quando não tratadas, degradando a qualidade do embedding. Versões antigas de páginas não arquivadas explicitamente permanecem indexáveis.

**Resolução por grafo**: no momento da ingestão, o crawler deve seguir os links internos de cada página e criar chunks com referência cruzada via `parent_doc_id` e `linked_doc_ids`. Páginas referenciadas são indexadas com metadado de origem (`referenced_by`), permitindo que o retriever expanda o contexto ao detectar dependências explícitas de conteúdo.

### Planilhas com fórmulas interdependentes

Células com fórmulas não carregam semântica — o embedding vê sintaxe, não valor calculado nem lógica de negócio. Dependências entre arquivos externos (ex: `frete-base-AAAAMM.xlsx` referenciado no PROC-042) quebram a cadeia de resolução. Planilhas com atualização mensal exigem estratégia de invalidação incremental, inexistente em pipelines ingênuos.

**Estratégia de serialização**: no momento da ingestão, cada célula com fórmula deve ser serializada com três campos: `formula` (sintaxe original), `computed_value` (valor calculado no momento da ingestão) e `snapshot_date` (data do cálculo). O embedding é gerado sobre o valor calculado, não sobre a sintaxe. Dependências externas devem ser resolvidas antes da ingestão; arquivos não resolvidos bloqueiam a ingestão do documento dependente.

### Agravante transversal — conflito de versões na base

Os documentos PROC-042 v1 e v2 coexistem sem marcação de obsolescência no SharePoint, com multiplicadores regionais, fatores de peso e prazos divergentes. O retriever é cego à autoridade dos documentos: trata o FAQ informal (sem responsável, sem validação de Compliance) com o mesmo peso que normativas oficiais. Isso representa o risco de maior impacto na qualidade das respostas.


## 3. Impacto na Qualidade das Respostas

| Sintoma observável | Causa raiz |
|---|---|
| Cálculo de frete incorreto | Versão errada do PROC-042 recuperada, ou ambas mescladas silenciosamente pelo LLM |
| SLA prometido incorretamente | Chunk com tabela parcial — tier do cliente ausente |
| Processo informal apresentado como política | FAQ com peso igual ao de documentos normativos |
| Omissão de exceções críticas | Regra geral e exceção em chunks separados; apenas a regra é recuperada |
| Respostas inconsistentes entre sessões | Retriever retorna chunks diferentes para a mesma pergunta |
| Alucinação sobre seguro de carga e carga danificada | Gaps documentais reais — esses processos não estão formalmente documentados |

---

## 4. Capacidade de Contexto e *Lost in the Middle*

Com GPT-4o (128K tokens), descontando system prompt (~2K), pergunta (~0,2K), histórico (~10K) e resposta (~2K), restam aproximadamente **114K tokens por query** — equivalente a **~227 chunks de 500 tokens**. Esse teto teórico é enganoso.

Pesquisas sobre o efeito *lost in the middle* demonstram que a atenção do modelo é significativamente maior nas posições inicial e final do contexto, degradando para o conteúdo posicionado no meio. Na prática, chunks relevantes posicionados entre as posições 20 e 200 têm probabilidade substancialmente menor de influenciar a resposta.

Para o caso da Novatech — com documentos conflitantes que podem ser recuperados simultaneamente — colocar PROC-042 v1 e v2 no meio de um contexto longo é a condição ideal para o modelo mesclar silenciosamente os valores das duas versões.

**Estratégia de posicionamento**: o chunk mais relevante deve ser posicionado na **primeira posição** do contexto, explorando a zona de alta atenção inicial. Chunks de suporte devem ocupar as **últimas posições**, aproveitando a zona de atenção final. O miolo do contexto (posições intermediárias) deve ser reservado para material de apoio de menor criticidade. Para documentos conflitantes como PROC-042 v1/v2, a solução correta é filtrar a versão obsoleta via metadata **antes** de montar o contexto — não confiar apenas no posicionamento.

> **Meta operacional recomendada: 5 a 10 chunks de alta precisão, não 227 chunks de relevância média.**


## 5. Seleção do Modelo de Embedding

A escolha do modelo de embedding é decisão crítica para uma base em português com terminologia especializada de logística e fretes.

| Modelo | Dimensões | Multilíngue | Indicado para |
|---|---|---|---|
| `text-embedding-3-large` (OpenAI) | 3072 | Sim | Alta qualidade geral; custo por query |
| `multilingual-e5-large` | 1024 | Sim | On-premise; bom custo-benefício para PT-BR |
| `intfloat/e5-mistral-7b-instruct` | 4096 | Parcial | Máxima qualidade; custo computacional alto |
| Fine-tuning em domínio | Variável | — | Melhor recall para terminologia específica |

**Recomendação**: iniciar com `multilingual-e5-large` para validação e, após coleta de 200+ pares query/documento relevante do domínio Novatech, avaliar fine-tuning. Modelos com mais de 1536 dimensões aumentam o storage e a latência de busca sem ganho proporcional nesse volume (~7K chunks).


## 6. Estratégia de Chunking Recomendada

A estratégia deve ser orientada pelo tipo de pergunta que o usuário fará, não por tamanho fixo de tokens:

| Padrão de conteúdo | Regra de chunking | Justificativa |
|---|---|---|
| Texto corrido | 500 tokens com overlap de ~75 tokens | Preserva continuidade entre seções adjacentes |
| Tabelas (qualquer tamanho) | Chunk atômico — tabela inteira | Metade de uma tabela não tem valor semântico |
| Regra + exceções | Obrigatoriamente no mesmo chunk | Perguntas sobre elegibilidade exigem ambos |
| Procedimento sequencial | Lista completa no mesmo chunk | Passos isolados perdem o fluxo do processo |
| Fórmula de cálculo | Fórmula + todas as tabelas de parâmetros juntas | Cálculo exige fórmula e seus insumos simultaneamente |

**Chunking semântico**: para texto corrido, além do tamanho fixo, utilizar detecção de fronteiras semânticas (mudança de assunto detectada por embedding de sentenças consecutivas) evita que chunks fixos partam no meio de um argumento coeso. LangChain `SemanticChunker` ou implementação equivalente.

Todo chunk deve carregar prefixo de metadado com `doc_id`, `versão`, `vigência`, `tipo` (normativo / contratual / informal), `fonte` e `ocr_confidence` (quando aplicável). Sem esse prefixo, o LLM não distingue PROC-042 v1 de v2 dentro do contexto.

### Pipeline de retrieval em três estágios

1. **Recall** — busca híbrida: vetorial (dense, top-50) + BM25/sparse (top-50), fusionados por RRF (*Reciprocal Rank Fusion*)
2. **Filtro de metadata** — remoção de chunks com `vigência` expirada, `ocr_confidence: low` em queries numéricas, e documentos marcados como obsoletos
3. **Precision** — reranking por cross-encoder (top 8–12 chunks finais para o contexto)

**Por que busca híbrida**: busca vetorial captura similaridade semântica mas perde em queries exatas como `"PROC-042"`, `"multiplicador 1.35"` ou nomes de campo específicos. BM25 é superior para correspondência exata de termos técnicos. A fusão via RRF combina os dois rankings sem necessidade de calibrar pesos manualmente.

Conflitos de versão devem ser resolvidos na camada de metadata — filtrando chunks obsoletos antes de montar o contexto — nunca delegando essa arbitragem ao LLM.


## 7. Guardrails para Gaps Documentais

Os gaps identificados (carga danificada, seguro de carga, frete abaixo de 500kg) exigem um mecanismo técnico explícito, não apenas instrução no system prompt.

**Implementação em dois níveis**:

1. **Classificador de intent pré-retrieval**: modelo leve (ex: `text-classification` fine-tunado) que detecta queries sobre tópicos sem cobertura documental e as encaminha diretamente para o fluxo de escalonamento humano, sem acionar o pipeline RAG.

2. **Verificação pós-retrieval por threshold**: se nenhum chunk retornado pelo reranker atingir similaridade mínima de 0,75 (calibrar empiricamente), o sistema não deve gerar resposta — deve retornar mensagem padronizada de encaminhamento ao responsável, registrando o tópico da query para análise de gaps.

O system prompt deve reforçar a instrução, mas nunca ser o único mecanismo de contenção.


## 8. Latência e Caching

O pipeline em três estágios adiciona latência que deve ser endereçada explicitamente:

| Etapa | Latência estimada |
|---|---|
| Embedding da query | 50–100ms |
| Busca vetorial (Qdrant/pgvector, 7K chunks) | 10–30ms |
| BM25 + RRF | 20–50ms |
| Filtro de metadata | < 5ms |
| Cross-encoder reranking (top-50 → top-10) | 150–400ms |
| Geração LLM (GPT-4o) | 800–2000ms |
| **Total estimado** | **1,0–2,6s** |

Para SLA de atendimento, o gargalo aceitável é geralmente < 3s de resposta total. O cross-encoder é o componente mais custoso fora do LLM.

**Estratégias de mitigação**:
- Cache semântico de queries frequentes: queries com embedding similar ao de uma query já respondida (threshold > 0,95) retornam a resposta cacheada sem acionar o pipeline completo. Implementável com Redis + índice vetorial auxiliar.
- Reranker quantizado (INT8) reduz latência do cross-encoder em ~40% com degradação mínima de qualidade.
- Streaming da resposta do LLM mascara parte da latência percebida pelo usuário.


## 9. Framework de Avaliação

Sem métricas objetivas, não é possível validar se ajustes de chunking, modelo de embedding ou threshold do reranker estão melhorando ou degradando a qualidade. O go-live deve ser precedido de avaliação estruturada.

**Métricas RAGAS recomendadas**:

| Métrica | O que mede | Meta mínima |
|---|---|---|
| Context Recall | % da resposta correta coberta pelos chunks recuperados | > 0,80 |
| Context Precision | % dos chunks recuperados que são realmente relevantes | > 0,75 |
| Faithfulness | % das afirmações da resposta suportadas pelos chunks | > 0,90 |
| Answer Relevancy | Alinhamento da resposta com a pergunta feita | > 0,85 |

**Dataset de avaliação**: construir 100–150 pares (pergunta, resposta esperada, chunks relevantes) cobrindo os cenários críticos: cálculo de frete, SLAs, elegibilidade, processos sequenciais e queries sobre gaps documentais. Esse dataset deve ser mantido e expandido após o go-live com casos reais.


## 10. Viabilidade Técnica

A implementação é viável com ferramentas amplamente disponíveis. O índice vetorial resultante (~7.000 chunks, ~42MB de embeddings com `multilingual-e5-large` 1024d) é de escala modesta — um único nó de Qdrant ou pgvector suporta com margem. O gargalo não é infraestrutura, é **qualidade do pipeline de ingestão e resolução dos conflitos documentais na fonte**.

Quatro pré-condições são bloqueantes para a qualidade mínima aceitável:

1. **Resolução do conflito PROC-042** — marcar v1 como obsoleta no SharePoint e no índice antes do go-live.
2. **Classificação de autoridade dos documentos** — FAQ informal não pode concorrer com normativas no retrieval para perguntas sobre valores, prazos e elegibilidade.
3. **Documentação dos gaps** — os processos de carga danificada, seguro de carga e frete padrão (abaixo de 500kg) não estão documentados formalmente. O assistente deve ser instruído explicitamente a não responder sobre esses tópicos e encaminhar ao responsável.
4. **Dataset de avaliação (golden set)** — sem métricas de linha de base pré-go-live, não há como detectar regressões após atualizações da base documental ou do pipeline.

> Sem essas quatro condições, o pipeline tecnicamente funcional ainda produzirá respostas incorretas com alta confiança aparente — o pior cenário para um assistente de atendimento ao cliente.

---

*Documento elaborado com base na documentação simulada da Novatech (Anexo A) e nos parâmetros técnicos do exercício Fase 1. A v2 incorpora revisão técnica de arquitetura RAG com foco em lacunas identificadas na v1: modelo de embedding, busca híbrida, avaliação e guardrails. A v3 corrige erro aritmético no multiplicador da base vs. janela de contexto do GPT-4o. A v4 detalha a metodologia de estimativa de tokens com separação explícita entre dados fornecidos e premissas adotadas.*
