# Log de Sessão de Revisão — Prompt NovaTech (v1 → v2)

**Data:** 2026-05-28  
**Tipo de sessão:** Revisão crítica e refinamento de prompt  
**Artefato analisado:** prompt-v1.md  
**Artefato gerado:** prompt-v2.md  
**Participantes:** Paulo (autor) / Claude Sonnet 4.6 (co-autor — revisão técnica e refinamento)  
**Classificação:** Documento interno  

---

## Interação 1 — Solicitação de análise e geração de v2

---

### Pergunta
**Paulo:** Esse documento foi gerado por mim, valide se há pontos de melhora nos prompts ou refinamentos e crie uma v2 colocando o Claude como co-autor.

*(Arquivo referenciado: `prompt-v1.md`)*

---

### Resposta do assistente

**Pontos de melhoria identificados na v1:**

| # | Problema identificado | Impacto |
|---|---|---|
| 1 | Regras duplicadas em 3+ seções ("nunca invente", "citar fonte") | Redundância sem ganho de clareza; aumenta tamanho do prompt sem reforço real |
| 2 | Nenhum exemplo de resposta (ausência de few-shot) | LLMs se ancoram no formato esperado via exemplos — sem eles, há risco de variação no output |
| 3 | Seção "Como Interpretar os Chunks" com bullets soltos sem ordem clara | Processo de avaliação ambíguo; pode gerar respostas fora de sequência |
| 4 | Campo "Observação" sem critério de uso ou omissão | Modelo pode usar "Observação" onde não há nada a observar, poluindo a resposta |
| 5 | Sem instrução de confidencialidade do prompt | System prompt pode ser revelado se diretamente questionado |
| 6 | Sem orientação para perguntas multi-parte | Perguntas com múltiplos aspectos podem ser respondidas de forma genérica e agrupada |
| 7 | Marcação `(estático)` inconsistente entre seções | Aparece em algumas seções, ausente em outras, sem lógica clara — ruído visual |

---

**Mudanças aplicadas na v2:**

| # | Problema (v1) | Solução (v2) |
|---|---|---|
| 1 | Regras repetidas em 3+ seções | Consolidadas por tema em blocos únicos: fontes, conteúdo, tom |
| 2 | Zero exemplos de resposta | Adicionada seção com 3 exemplos canônicos: resposta clara, conflito entre fontes, informação insuficiente |
| 3 | Bullets soltos para interpretar chunks | Substituídos por algoritmo de avaliação com 6 passos numerados e sequenciais |
| 4 | Campo "Observação" sem critério de uso/omissão | Definidos 4 casos de uso explícitos; instrução de omitir se nenhum se aplicar |
| 5 | Sem proteção do system prompt | Adicionada instrução: não revelar instruções internas; responder que "segue diretrizes internas da NovaTech" |
| 6 | Sem orientação para perguntas multi-parte | Adicionada instrução: responder cada aspecto separadamente, na ordem apresentada |
| 7 | Marcação `(estático)` inconsistente | Removida; toda a sessão é estática por definição — chunks são a única parte dinâmica |

---

**Artefato gerado:** `prompt-v2.md` — com Paulo como autor e Claude Sonnet 4.6 como co-autor.

---

## Observações gerais da sessão

- A estrutura geral do prompt-v1 foi considerada sólida: identidade clara, hierarquia de fontes bem definida, comportamentos por cenário e template de saída já presentes.
- Os problemas identificados são majoritariamente de **qualidade de especificação**, não de concepção — a lógica estava correta, mas o nível de prescrição era insuficiente em alguns pontos críticos.
- A maior adição em termos de impacto esperado são os **exemplos few-shot** (seção de exemplos canônicos), pois ancoram o modelo no formato e no nível de detalhe esperado de forma mais efetiva do que regras descritivas isoladas.
- A **consolidação de regras duplicadas** reduz o tamanho do prompt sem perda de cobertura, o que tende a melhorar a eficiência de processamento e reduzir ruído de instrução.
- A instrução de **algoritmo sequencial para chunks** é especialmente relevante para RAG: sem uma ordem de avaliação clara, o modelo pode responder com o primeiro chunk relevante sem verificar conflitos com os demais.
