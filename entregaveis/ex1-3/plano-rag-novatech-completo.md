# Plano Completo da Pipeline RAG - NovaTech

## 1. Objetivo
Este documento consolida o plano completo da pipeline RAG para a NovaTech, cobrindo ingestao, busca e montagem de prompts, com justificativas para cada decisao tecnica e rastreabilidade de autoria das decisoes.

Objetivo operacional:
- Reduzir tempo de busca do atendente.
- Aumentar consistencia e rastreabilidade das respostas.
- Tratar conflitos documentais sem arbitragem indevida.

## 2. Escopo e fontes consideradas
### 2.1 Fontes de entrada
- anexo-a-documentos-individuais/POL-001-politica-devolucao.md
- anexo-a-documentos-individuais/PROC-042-frete-especial-v1.md
- anexo-a-documentos-individuais/PROC-042-v2-frete-especial-revisado.md
- anexo-a-documentos-individuais/SLA-2024-tabela-sla-clientes.md
- anexo-a-documentos-individuais/FAQ-atendimento.md

### 2.2 Regras de prioridade de fonte
As regras de prioridade foram herdadas da versao v3 do prompt:
- entregaveis/ex1-2/prompt-v3.md

Principio-chave: FAQ e material informal nunca sobrepoem documento oficial.

## 3. Decisoes consolidadas (com autoria)
### 3.1 Decisoes suas (usuario)
1. Estrategia de chunking: Estrategia C (hibrida).
- Justificativa: melhor equilibrio entre coerencia semantica e controle de tamanho.

2. Regra de prioridade entre fontes em caso de conflito.
- Justificativa: governanca explicita para evitar consolidacao arbitraria de documentos contraditorios.

3. Modelo de embedding: paraphrase-multilingual-MiniLM-L12-v2.
- Justificativa: base em portugues, com melhor adequacao semantica multilíngue.

### 3.2 Decisoes minhas (assistente)
1. Ingerir PROC-042 v1 e v2 simultaneamente, com metadados de vigencia.
- Justificativa: preserva historico e permite aplicar regra de transicao temporal da v2.

2. Reordenar resultados de retrieval por prioridade de fonte apos similaridade.
- Justificativa: evita que fonte informal prevaleca por score vetorial puro.

3. Tratar FAQ como fonte auxiliar, nunca normativa.
- Justificativa: documento explicitamente informal e nao validado formalmente.

4. Re-ranking como opcional para evolucao, fora do MVP inicial.
- Justificativa: reduz complexidade da primeira entrega e permite iteracao guiada por metricas.

## 4. Stack tecnica definida
- Linguagem: Python
- Vector store: ChromaDB local
- Embeddings: sentence-transformers com paraphrase-multilingual-MiniLM-L12-v2
- Orquestracao: LangChain

Justificativa geral:
- Atende ao requisito do exercicio.
- Stack gratuita e open-source para PoC.
- Facil evolucao para arquitetura gerenciada no futuro.

## 5. Arquitetura da pipeline
Fluxo de alto nivel:
1. Ingestao offline dos documentos.
2. Geração de embeddings e persistencia vetorial.
3. Busca por similaridade na consulta.
4. Filtro/reordenacao por autoridade documental.
5. Montagem do prompt com rastreabilidade.
6. Geração da resposta pelo LLM.

## 6. Etapa 1 - Ingestao
### 6.1 Leitura dos documentos
Ler arquivos Markdown e transformar em objetos de documento com conteudo e metadados.

### 6.2 Enriquecimento de metadados
Campos minimos por chunk:
- source
- doc_id
- doc_type
- version
- last_updated
- authority_label
- priority_level
- has_transition_rule
- valid_from
- section_heading
- chunk_method
- chunk_index_in_section

Justificativa:
- Permite auditoria, filtros de retrieval e governanca de conflito.

### 6.3 Chunking definido (Estrategia C)
Regra:
1. Quebra primaria por heading Markdown (secoes).
2. Se uma secao ultrapassar o limite, aplicar subdivisao recursiva com overlap.

Parametros iniciais:
- threshold de subdivisao: 1000 caracteres
- chunk_size: 700
- chunk_overlap: 100

Justificativa:
- Preserva semantica por secao.
- Evita chunks grandes demais.
- Mantem continuidade com overlap.

### 6.4 Embeddings
Gerar embeddings com paraphrase-multilingual-MiniLM-L12-v2.

Justificativa:
- Melhor alinhamento ao idioma da base (PT-BR).

### 6.5 Persistencia
Persistir chunks + embeddings + metadados no ChromaDB com armazenamento local.

Justificativa:
- Simplicidade operacional no MVP.
- Reuso da base em consultas subsequentes.

## 7. Etapa 2 - Busca (Retrieval)
### 7.1 Busca inicial por similaridade
Converter pergunta em embedding e recuperar top-k chunks no ChromaDB.

### 7.2 Filtros de autoridade e vigencia
Aplicar filtros por metadata:
- excluir vigencia expirada quando aplicavel;
- reduzir uso de fonte informal em consultas normativas.

### 7.3 Reordenacao por prioridade de fonte
Apos similaridade, ordenar por prioridade documental definida.

Justificativa:
- Combina relevancia semantica com confiabilidade da fonte.

### 7.4 Re-ranking (opcional)
Nao obrigatorio no MVP.

Justificativa:
- Pode melhorar precisao, mas com custo de latencia/complexidade.

## 8. Etapa 3 - Montagem do prompt
### 8.1 Estrutura recomendada
1. Instrucoes do sistema.
2. Chunks recuperados com metadados visiveis.
3. Pergunta do usuario.

### 8.2 Rotulacao de contexto
Cada trecho deve expor origem e natureza da fonte:
- documento
- versao
- autoridade
- prioridade

Justificativa:
- Suporta rastreabilidade e reduz risco de uso indevido de fonte informal.

### 8.3 Controle de contexto
Limitar tamanho total de contexto e priorizar chunks mais confiaveis.

Justificativa:
- Mitiga perda de qualidade em contextos excessivos.

## 9. Tratamento de conflito documental
### 9.1 Ordem de prioridade aplicada
1. Instrucoes do system prompt.
2. Normativo/contratual formal.
3. Procedimento oficial com versao/data/vigencia.
4. Documento oficial mais recente com vigencia clara.
5. Conflito sem hierarquia/vigencia: nao arbitrar, escalar.
6. Fonte informal: apoio, nunca normativa.

### 9.2 Regras adicionais aplicadas
- Regra de transicao explicita prevalece sobre data isolada.
- Versoes sem vigencia inequívoca nao devem ser consolidadas.
- Se apenas fonte informal responder, declarar ausencia de respaldo oficial.

Justificativa:
- Evita alucinacao normativa.
- Cria comportamento previsivel para QA e operacao.

## 10. Caso critico: PROC-042 v1 x v2
Decisao aplicada:
- Ingerir ambas as versoes.
- Usar metadados de vigencia e transicao.
- Aplicar regra temporal quando data do chamado estiver disponivel.
- Sem dado temporal suficiente, informar conflito e pedir validacao humana.

Justificativa:
- A propria v2 explicita regra transitoria.
- Evita simplificacao incorreta de sempre usar a versao mais recente.

## 11. Qualidade, risco e governanca
### 11.1 Riscos principais
- Mistura de versoes conflitantes.
- Uso indevido de FAQ informal como regra oficial.
- Recuperacao parcial de tabela/regra sem excecoes.

### 11.2 Mitigacoes previstas
- Metadados ricos por chunk.
- Regras de prioridade no retrieval e prompt.
- Estrategia de chunking semantica por secao + subdivisao controlada.

## 12. Escopo de entrega
### 12.1 MVP
- Ingestao dos 5 documentos.
- Busca vetorial com filtros de autoridade.
- Montagem de prompt com rastreabilidade.

### 12.2 Evolucoes
- Re-ranking por cross-encoder.
- Testes automatizados de retrieval/generacao.
- Ingestao incremental por hash de documento.
- Observabilidade com logs de consulta/chunks/resposta.

## 13. Resumo executivo
O plano final atende aos requisitos do exercicio e esta tecnicamente coerente com o contexto da NovaTech. As decisoes criticas estao formalizadas com autoria explicita (usuario vs assistente), preservando rastreabilidade de governanca e justificativas de arquitetura.
