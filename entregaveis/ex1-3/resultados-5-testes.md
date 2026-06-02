# Resultados dos 5 Testes — Pipeline RAG NovaTech
**Data de execução:** 30/05/2026  
**Perguntas:** extraídas do mapa de cobertura do Anexo B  
**Script:** `src/test_runner.py` (saídas individuais em `outputs/testes/`)

---

## Tabela resumo

| # | Pergunta | Chunk obrigatório recuperado? | Match Anexo B | Avaliação Claude |
|---|---|---|---|---|
| T1 | Qual o prazo de devolução? | ✗ (POL-001-B ausente) | Parcial | Incompleta — exceções não aparecem |
| T2 | Posso devolver carga perigosa? | ✓ (POL-001-B rank 2) | Correto | Correta — armadilha tratada |
| T3 | Qual o SLA do cliente Gold? | ✗ (SLA-2024-B ausente) | Falhou | Incompleta — tabela não recuperada |
| T4 | Qual o SLA do cliente Platinum? | ✓ (SLA-2024-A rank 2) | Correto | Correta — trap de tier inexistente tratado |
| T5 | Qual o multiplicador para o Sudeste? | ✓ (PROC-042v2-B rank 1) | Correto c/ risco | Conflito identificado, sem regra temporal |

**Resultado geral: 3/5 corretos** (T2, T4, T5 — T1 e T3 com falhas reais)

---

## Teste 1 — "Qual o prazo de devolução?"

### Chunks recuperados pelo pipeline

| Rank | Score | Fonte | Seção | Prioridade |
|------|-------|-------|-------|------------|
| 1 | 0.8086 | POL-001-politica-devolucao.md | 3.1. Prazo geral | 2 |
| 2 | 1.0728 | SLA-2024-tabela-sla-clientes.md | 5. Medição e reportes | 2 |
| 3 | 1.0731 | POL-001-politica-devolucao.md | root | 2 |
| 4 | 1.0789 | POL-001-politica-devolucao.md | 3.5. Custos de devolução | 2 |
| 5 | 0.9073 | PROC-042-v2-frete-especial-revisado.md | 3. Prazo de entrega para frete especial | 3 |
| 6 | 0.9502 | PROC-042-frete-especial-v1.md | 3. Prazo de entrega para frete especial | 3 |

### Gabarito Anexo B

| Chunk esperado | Presente? | Observação |
|---|---|---|
| POL-001-A (seção 3.1 — prazo geral) | ✓ rank 1 | Recuperado corretamente |
| POL-001-B (seção 3.2 — exceções) | **✗ ausente** | Crítico: exceções para cargas perigosas não aparecem |

### Resposta do Claude

Com base nos chunks recuperados, Claude responde:

> **Resposta:** O prazo geral para solicitação de devolução é de 7 (sete) dias úteis a partir da data de recebimento confirmada no sistema de tracking, com a contagem excluindo sábados, domingos e feriados nacionais.
>
> **Fonte:**
> - POL-001 — Política de Devolução, Seção 3.1 — Prazo geral
>
> **Observação:** Os chunks recuperados não incluem a seção de exceções (3.2). Não é possível confirmar com os dados disponíveis se o item em questão se enquadra em alguma categoria de exceção ao prazo geral. Recomendo verificar se a carga é perigosa, refrigerada ou tem lacre de segurança, pois essas categorias possuem tratamento diferenciado conforme a política.

**Avaliação:**
- Correta? **Parcialmente** — o prazo geral está correto, mas as exceções da seção 3.2 (cargas perigosas, etc.) não foram recuperadas e estão ausentes da resposta.
- Citou fonte? ✓
- Respeitou guardrails? ✓ — não inventou exceções, alertou sobre limitação
- **Risco real:** atendente que recebe esta resposta pode não saber que carga perigosa não é elegível para devolução padrão.

---

## Teste 2 — "Posso devolver carga perigosa?"

### Chunks recuperados pelo pipeline

| Rank | Score | Fonte | Seção | Prioridade |
|------|-------|-------|-------|------------|
| 1 | 1.1030 | POL-001-politica-devolucao.md | 3.5. Custos de devolução | 2 |
| 2 | 1.1489 | POL-001-politica-devolucao.md | 3.2. Exceções ao prazo geral | 2 |
| 3 | 1.0713 | PROC-042-v2-frete-especial-revisado.md | 4. Condições especiais | 3 |
| 4 | 1.1406 | PROC-042-frete-especial-v1.md | 4. Condições especiais | 3 |
| 5 | 0.9245 | FAQ-atendimento.md | Item 38 — carga danificada | 6 |
| 6 | 1.0095 | FAQ-atendimento.md | Item 3 — carga perigosa | 6 |

### Gabarito Anexo B

| Chunk esperado | Presente? | Observação |
|---|---|---|
| POL-001-B (seção 3.2 — exceções) | ✓ rank 2 | Recuperado |
| FAQ-03 (orientação informal) | ✓ rank 6 | Opcional — presente |

### Resposta do Claude

> **Resposta:** Cargas perigosas classificadas nas classes 1 a 6 da ANTT **não são elegíveis para devolução pelo processo padrão**. Isso inclui explosivos (classe 1), gases (classe 2), líquidos inflamáveis (classe 3), sólidos inflamáveis (classe 4), oxidantes e peróxidos (classe 5) e substâncias tóxicas e infectantes (classe 6), conforme a Resolução ANTT nº 5.947/2021. Para essas categorias, o cliente deve entrar em contato com o setor de Gestão de Riscos pelo ramal 4500 para tratamento individual.
>
> **Fonte:**
> - POL-001 — Política de Devolução, Seção 3.2 — Exceções ao prazo geral
> - FAQ Atendimento, Item 3 — Devolução de carga perigosa (fonte informal, não validada formalmente)
>
> **Observação:** O documento oficial veda o processo padrão, mas não declara impossível em todos os cenários. O FAQ interno (não validado formalmente) indica que o setor de Gestão de Riscos já autorizou exceções em casos anteriores. O encaminhamento correto é sempre o ramal 4500.

**Avaliação:**
- Correta? ✓ — resposta principal precisa, armadilha tratada corretamente
- Citou fonte? ✓ — oficial e informal com distinção de rótulo
- Respeitou guardrails? ✓ — não consolida informal como normativo
- Ruído detectado: FAQ-38 (carga danificada) apareceu no rank 5 mas não foi usado na resposta — sistema prompt filtrou corretamente.

---

## Teste 3 — "Qual o SLA do cliente Gold?"

### Chunks recuperados pelo pipeline

| Rank | Score | Fonte | Seção | Prioridade |
|------|-------|-------|-------|------------|
| 1 | 1.1209 | SLA-2024-tabela-sla-clientes.md | 5. Medição e reportes | 2 |
| 2 | 1.1626 | SLA-2024-tabela-sla-clientes.md | root | 2 |
| 3 | 1.2376 | SLA-2024-tabela-sla-clientes.md | 4. Penalidades por descumprimento | 2 |
| 4 | 1.3487 | SLA-2024-tabela-sla-clientes.md | 1. Classificação de clientes | 2 |
| 5 | 1.3908 | POL-001-politica-devolucao.md | 2. Escopo | 2 |
| 6 | 1.3951 | POL-001-politica-devolucao.md | 3.3. Procedimento de devolução | 2 |

### Gabarito Anexo B

| Chunk esperado | Presente? | Observação |
|---|---|---|
| SLA-2024-B (seção 2 — tabela de SLAs) | **✗ ausente** | Chunk mais importante não recuperado |
| SLA-2024-A (seção 1 — classificação) | ✓ rank 4 | Recuperado, mas não responde à pergunta |

### Resposta do Claude

> **Resposta:** Não encontrei informação suficiente na documentação disponível para responder com segurança. Os chunks recuperados cobrem as seções de medição e reportes, classificação de tiers e penalidades do SLA-2024, mas não incluem a tabela de métricas de tempo de resposta e resolução para chamados gerais ou incidentes críticos.
>
> **Fonte:**
> - SLA-2024 — Tabela de SLA por Tipo de Cliente, Seção 5 — Medição e reportes
> - SLA-2024 — Tabela de SLA por Tipo de Cliente, Seção 1 — Classificação de clientes
>
> **Observação:** A seção 2 do SLA-2024 (tabela de tempos de resposta por tier) não foi recuperada nesta consulta. Recomendo escalar para o supervisor ou consultar diretamente o documento SLA-2024, seção 2.

**Avaliação:**
- Correta? ✗ — **falha de retrieval**. A tabela de SLAs (seção 2) não foi recuperada. A informação existe no documento mas não chegou ao LLM.
- Citou fonte? ✓ — citou o que tinha
- Respeitou guardrails? ✓ — não inventou SLAs, escalou corretamente
- **Causa raiz:** formato tabular da seção 2 (`| Gold | 2h úteis | ...`) não embeda bem semanticamente — o modelo não captura a relação entre cabeçalho de coluna e célula de valor.

---

## Teste 4 — "Qual o SLA do cliente Platinum?"

### Chunks recuperados pelo pipeline

| Rank | Score | Fonte | Seção | Prioridade |
|------|-------|-------|-------|------------|
| 1 | 1.0393 | SLA-2024-tabela-sla-clientes.md | root | 2 |
| 2 | 1.2689 | SLA-2024-tabela-sla-clientes.md | 1. Classificação de clientes | 2 |
| 3 | 1.2969 | SLA-2024-tabela-sla-clientes.md | 5. Medição e reportes | 2 |
| 4 | 1.3036 | POL-001-politica-devolucao.md | 2. Escopo | 2 |
| 5 | 1.2007 | PROC-042-v2-frete-especial-revisado.md | root | 3 |
| 6 | 1.2456 | PROC-042-frete-especial-v1.md | root | 3 |

### Gabarito Anexo B

| Chunk esperado | Presente? | Observação |
|---|---|---|
| SLA-2024-A (seção 1 — "não existem outros tiers") | ✓ rank 2 | Recuperado corretamente |
| FAQ-15 (tier Platinum) | ✗ ausente | Opcional — filtrado por prioridade, não impacta |

### Resposta do Claude

> **Resposta:** Não existe tier "Platinum" na NovaTech. Os tiers de cliente são três: Gold, Silver e Standard. Solicitações de SLA diferenciado fora desses tiers devem ser encaminhadas ao Comercial para análise de viabilidade.
>
> **Fonte:**
> - SLA-2024 — Tabela de SLA por Tipo de Cliente, Seção 1 — Classificação de clientes

**Avaliação:**
- Correta? ✓ — tier inexistente corretamente identificado, sem alucinação de SLAs inventados
- Citou fonte? ✓
- Respeitou guardrails? ✓ — não inventou valores para tier inexistente
- Ruído: PROC-042 root (ranks 5 e 6) irrelevante, mas não usado na resposta.

---

## Teste 5 — "Qual o multiplicador para o Sudeste?"

### Chunks recuperados pelo pipeline

| Rank | Score | Fonte | Seção | Prioridade |
|------|-------|-------|-------|------------|
| 1 | 0.6839 | PROC-042-v2-frete-especial-revisado.md | 2.1. Multiplicadores regionais (nov/2023) | 3 |
| 2 | 0.7808 | PROC-042-frete-especial-v1.md | 2.1. Multiplicadores regionais | 3 |
| 3 | 1.1708 | PROC-042-v2-frete-especial-revisado.md | 1. Objetivo | 3 |
| 4 | 1.2550 | PROC-042-frete-especial-v1.md | 2. Fórmula de cálculo | 3 |
| 5 | 1.2676 | PROC-042-v2-frete-especial-revisado.md | 2. Fórmula de cálculo | 3 |
| 6 | 1.0632 | FAQ-atendimento.md | Item 8 — frete especial | 6 |

### Gabarito Anexo B

| Chunk esperado | Presente? | Observação |
|---|---|---|
| PROC-042v2-B (multiplicadores atualizados) | ✓ rank 1 | Recuperado como mais similar |
| PROC-042-B (versão antiga — risco de contradição) | ✓ rank 2 | Presente — conflito v1 vs v2 ativado |

### Resposta do Claude

> **Resposta:** Há duas versões do procedimento PROC-042 com valores diferentes para o multiplicador regional do Sudeste:
> - **PROC-042 v1 (versão original):** Sudeste — multiplicador 1.0
> - **PROC-042 v2 (revisado em novembro/2023):** Sudeste — multiplicador 1.1
>
> As duas versões coexistem nos documentos disponíveis. Dado que a v2 é mais recente (novembro/2023) e não há evidência explícita de uma regra de transição nos chunks recuperados, não é possível determinar com segurança qual versão se aplica sem saber a data de abertura do chamado.
>
> **Fonte:**
> - PROC-042 — Frete Especial, Seção 2.1 — Multiplicadores regionais (versão original)
> - PROC-042-v2 — Frete Especial Revisado, Seção 2.1 — Multiplicadores regionais (novembro/2023)
>
> **Observação:** Conflito entre versões sem regra de vigência explícita nos chunks disponíveis. Recomendo verificar se o chamado foi aberto antes ou após 01/12/2023 — isso determina qual tabela aplicar. Escalar para o supervisor se a data não estiver disponível.

**Avaliação:**
- Correta? ✓ parcialmente — identifica o conflito e não consolida arbitrariamente
- Citou fonte? ✓ — ambas as versões com distinção clara
- Respeitou guardrails? ✓ — não escolheu uma versão sem evidência
- **Risco:** A seção 5 da PROC-042-v2 (disposições transitórias: "chamados antes de 01/12/2023 → usar v1") não foi recuperada. A regra de transição existe no documento mas não chegou ao contexto.

---

## Problemas reais identificados

### Problema 1 — Ruído semântico por sobreposição de keyword "prazo"

**Observado em:** Teste 1 ("Qual o prazo de devolução?")

**O que aconteceu:** Chunks do PROC-042 sobre "Prazo de entrega para frete especial" (ranks 5 e 6) foram recuperados para uma pergunta sobre prazo de *devolução*. São documentos completamente diferentes — um trata de logística de entrega, o outro de política de retorno de mercadorias. A palavra "prazo" causou falso positivo semântico.

**Consequência real:** POL-001-B (seção 3.2 — exceções ao prazo geral, onde estão as cargas perigosas) ficou fora do top-6 porque foi deslocado pelos chunks irrelevantes do PROC-042. Um atendente que use essa resposta não receberá a informação de que cargas perigosas têm tratamento diferenciado.

**Proposta de correção:** Dois caminhos complementares:
1. **Filtro por domínio no metadata**: adicionar campo `domain` nos metadados (ex: `"devolucao"`, `"frete"`, `"sla"`) e incluir filtro no retrieval quando a pergunta contiver termos de um domínio específico — bloquear chunks de domínio diferente.
2. **Aumentar top_k para 10**: recuperar mais chunks e confiar mais no re-ranking por autoridade, aumentando a chance de POL-001-B aparecer.

---

### Problema 2 — Tabela markdown não embeda semanticamente

**Observado em:** Teste 3 ("Qual o SLA do cliente Gold?")

**O que aconteceu:** A seção 2 do SLA-2024 contém a tabela de métricas `| Gold | 2h úteis | ...`. Essa seção não apareceu no top-6. As seções de texto prosa (Medição, Penalidades, Classificação) foram recuperadas com scores melhores. O modelo de embedding `paraphrase-multilingual-MiniLM-L12-v2` não captura bem a relação entre cabeçalho de coluna e célula de valor em tabelas markdown.

**Consequência real:** Para a pergunta mais direta sobre SLAs ("Qual o SLA do cliente Gold?"), o chunk com a resposta existe mas não é recuperado. O LLM precisa acionar o guardrail de "informação insuficiente" — a resposta é segura mas não é útil.

**Proposta de correção:** Pré-processar tabelas markdown para formato textual antes do embedding. Transformar cada linha da tabela em texto prosa antes da ingestão. Exemplo de conversão: `| Gold | 2h úteis | 24h úteis |` → `"Para clientes Gold: tempo de primeira resposta de até 2 horas úteis, tempo de resolução de até 24 horas úteis (chamados gerais)."` Este formato embeda corretamente a relação semântica.

---

### Problema 3 — Regra de transição PROC-042v2-E não recuperada no conflito de versões

**Observado em:** Teste 5 ("Qual o multiplicador para o Sudeste?")

**O que aconteceu:** Tanto PROC-042-v1 (Sudeste: 1.0) quanto PROC-042-v2 (Sudeste: 1.1) foram recuperados com os menores scores de distância (0.68 e 0.78 — os mais similares do teste). O LLM recebe os dois valores conflitantes. Porém, a seção 5 da PROC-042-v2 — que contém a regra de transição explícita ("chamados abertos antes de 01/12/2023 devem usar os multiplicadores da versão anterior") — não foi recuperada.

**Consequência real:** O LLM aplica corretamente o guardrail de conflito (não consolida arbitrariamente), mas menciona a data 01/12/2023 apenas por inferência, sem a evidência textual direta. Um avaliador poderia questionar se essa data está sendo inventada.

**Proposta de correção:** Adicionar lógica de "co-retrieval por documento": quando um chunk de um documento versionado é recuperado (PROC-042-v2), recuperar forçadamente os chunks de seção especial do mesmo documento (seção 5 — disposições transitórias) independentemente do score semântico. Implementar como lista de seções âncora por documento: `ANCHOR_SECTIONS = {"PROC-042-v2": ["5. Disposições transitórias"]}`.

---

## Nota metodológica

Os resultados das respostas do Claude foram obtidos colando os prompts montados pelo pipeline (arquivos `outputs/testes/teste-XX-prompt.txt`) em uma conversa nova no Claude (claude.ai), utilizando o sistema de prompt da versão 3 carregada de `entregaveis/ex1-2/prompt-v3.md`. As respostas documentadas acima são fiéis ao output do Claude, com edição apenas para remoção de formatação de markdown aninhado.
