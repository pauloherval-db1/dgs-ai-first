# Implementacao da Pipeline RAG - Ex1-3

## Estrutura
- src/config.py: configuracoes globais da pipeline
- src/metadata_utils.py: extracao e enriquecimento de metadados
- src/chunking.py: estrategia C (header + recursive split)
- src/embedding.py: modelo de embedding definido (multilingual MiniLM L12 v2)
- src/ingest.py: ingestao e indexacao no ChromaDB
- src/retrieve.py: busca vetorial com filtro/reordenacao por prioridade
- src/prompt_builder.py: montagem de prompt com fontes e carregamento de template oficial
- src/main.py: orquestracao simples para gerar prompt final

## Como executar
1. Instalar dependencias:
   pip install -r entregaveis/ex1-3/requirements.txt

2. Rodar ingestao:
   python -m entregaveis.ex1-3.src.ingest

3. Testar retrieval:
   python -m entregaveis.ex1-3.src.retrieve

4. Montar prompt final:
   python -m entregaveis.ex1-3.src.main

## Observacoes
- O ChromaDB e persistido em: entregaveis/ex1-3/chroma_db
- A base de documentos usada vem de: anexo-a-documentos-individuais
- FAQ e tratado como fonte informal (prioridade inferior)
- O system prompt e carregado de: entregaveis/ex1-2/prompt-v3.md
