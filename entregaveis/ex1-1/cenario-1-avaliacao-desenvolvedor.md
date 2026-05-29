# Análise Técnica — Pipeline de RAG para Assistente de IA Novatech

**Data**: 28/05/2026  
**Autor** : Paulo + Claude  
**Classificação**: Documento técnico  

---

## 1. Contexto

A Novatech busca implantar um assistente de IA baseado em RAG (*Retrieval-Augmented Generation*) para suporte ao time de atendimento. A base de conhecimento é composta por ~800 documentos PDF (média de 10 páginas), ~400 páginas wiki no Confluence e ~50 planilhas, totalizando aproximadamente **3,6 milhões de tokens** (~4,3M com overhead de metadata e serialização estruturada).

Essa escala torna o RAG **obrigatório**: a base é 18 vezes maior que a janela de contexto do GPT-4o (128K tokens), inviabilizando qualquer abordagem de ingestão total por query.


## 2. Desafios por Tipo de Fonte

### PDFs com tabelas complexas

Parsers genéricos serializam tabelas em texto linear, destruindo o relacionamento linha×coluna. Tabelas partidas entre chunks tornam-se ininterpretáveis — o chunk sem cabeçalho não carrega informação útil. Para a Novatech, isso afeta diretamente os cálculos de frete (PROC-042) e a tabela de SLAs, podendo gerar valores numericamente incorretos com aparência de confiança.

### PDFs escaneados

OCR introduz ruído tipográfico sistemático em valores críticos (`1.O` vs `1.0`, erros em dígitos de multiplicadores e prazos). Fluxogramas embutidos como imagens são completamente ignorados pelo pipeline padrão — o conteúdo visual não entra no índice. A confiança variável por bloco OCR não é propagada ao retriever, que trata texto corrompido com o mesmo peso que texto íntegro.

### Wiki Confluence com links internos

Cada página é ingerida como documento isolado, mas links internos criam dependências implícitas de conteúdo — a página referenciada não é automaticamente trazida ao contexto. Macros customizadas (`{warning}`, `{expand}`, `{info}`) geram lixo textual quando não tratadas, degradando a qualidade do embedding. Versões antigas de páginas não arquivadas explicitamente permanecem indexáveis.

### Planilhas com fórmulas interdependentes

Células com fórmulas não carregam semântica — o embedding vê sintaxe, não valor calculado nem lógica de negócio. Dependências entre arquivos externos (ex: `frete-base-AAAAMM.xlsx` referenciado no PROC-042) quebram a cadeia de resolução. Planilhas com atualização mensal exigem estratégia de invalidação incremental, inexistente em pipelines ingênuos.

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

> **Meta operacional recomendada: 5 a 10 chunks de alta precisão, não 227 chunks de relevância média.**


## 5. Estratégia de Chunking Recomendada

A estratégia deve ser orientada pelo tipo de pergunta que o usuário fará, não por tamanho fixo de tokens:

| Padrão de conteúdo | Regra de chunking | Justificativa |
|---|---|---|
| Texto corrido | 500 tokens com overlap de ~75 tokens | Preserva continuidade entre seções adjacentes |
| Tabelas (qualquer tamanho) | Chunk atômico — tabela inteira | Metade de uma tabela não tem valor semântico |
| Regra + exceções | Obrigatoriamente no mesmo chunk | Perguntas sobre elegibilidade exigem ambos |
| Procedimento sequencial | Lista completa no mesmo chunk | Passos isolados perdem o fluxo do processo |
| Fórmula de cálculo | Fórmula + todas as tabelas de parâmetros juntas | Cálculo exige fórmula e seus insumos simultaneamente |

Todo chunk deve carregar prefixo de metadado com `doc_id`, `versão`, `vigência` e `tipo` (normativo / contratual / informal). Sem esse prefixo, o LLM não distingue PROC-042 v1 de v2 dentro do contexto.

### Pipeline de retrieval em dois estágios

1. **Recall** — busca vetorial ampla (top 50–100 candidatos por similaridade semântica)
2. **Precision** — reranking por cross-encoder (top 8–12 chunks finais para o contexto)

Conflitos de versão devem ser resolvidos na camada de metadata — filtrando chunks obsoletos antes de montar o contexto — nunca delegando essa arbitragem ao LLM. O chunk de maior relevância deve ser posicionado na **primeira posição do contexto**, explorando a zona de alta atenção do modelo.


## 6. Viabilidade Técnica

A implementação é viável com ferramentas amplamente disponíveis. O índice vetorial resultante (~7.000 chunks, ~42MB de embeddings) é de escala modesta — um único nó de Qdrant ou pgvector suporta com margem. O gargalo não é infraestrutura, é **qualidade do pipeline de ingestão e resolução dos conflitos documentais na fonte**.

Três pré-condições são bloqueantes para a qualidade mínima aceitável:

1. **Resolução do conflito PROC-042** — marcar v1 como obsoleta no SharePoint e no índice antes do go-live.
2. **Classificação de autoridade dos documentos** — FAQ informal não pode concorrer com normativas no retrieval para perguntas sobre valores, prazos e elegibilidade.
3. **Documentação dos gaps** — os processos de carga danificada, seguro de carga e frete padrão (abaixo de 500kg) não estão documentados formalmente. O assistente deve ser instruído explicitamente a não responder sobre esses tópicos e encaminhar ao responsável.

> Sem essas três condições, o pipeline tecnicamente funcional ainda produzirá respostas incorretas com alta confiança aparente — o pior cenário para um assistente de atendimento ao cliente.

---

*Documento elaborado com base na documentação simulada da Novatech (Anexo A) e nos parâmetros técnicos do exercício Fase 1.*
