# Log de Sessão de Teste — Assistente NovaTech
**Data:** 2026-05-28  
**Prompts testados:** prompt-v2.md (perguntas 1–10a) / prompt-v3.md (pergunta 10b — re-resposta corrigida)  
**Chunks utilizados:** Anexo B completo (POL-001, PROC-042, PROC-042-v2, SLA-2024, FAQ-Atendimento)

---

## Rodada 1 — Informação clara e exceções

---

### Pergunta 1
**Atendente:** Qual o prazo de devolução?

**Resposta do assistente (v2):**
> O prazo para solicitação de devolução é de **7 dias úteis** contados a partir da data de recebimento confirmada no sistema de tracking, excluindo sábados, domingos e feriados nacionais.
>
> **Fonte:**
> POL-001, Seção 3.1 — Prazo geral
>
> **Observação:**
> Cargas perigosas das classes 1 a 6 da ANTT (explosivos, gases, líquidos inflamáveis, sólidos inflamáveis, oxidantes/peróxidos, substâncias tóxicas/infectantes) **não são elegíveis** para devolução pelo processo padrão. Nesses casos, o cliente deve contatar o setor de Gestão de Riscos pelo ramal 4500 para tratamento individual.
> *(POL-001, Seção 3.2 — Exceções)*

---

### Pergunta 2
**Atendente:** Posso devolver carga perigosa?

**Resposta do assistente (v2):**
> Cargas perigosas das classes 1 a 6 da ANTT **não são elegíveis para devolução pelo processo padrão**, independentemente do prazo. Isso inclui explosivos (classe 1), gases (classe 2), líquidos inflamáveis (classe 3), sólidos inflamáveis (classe 4), oxidantes e peróxidos (classe 5), e substâncias tóxicas e infectantes (classe 6). O cliente deve contatar o setor de Gestão de Riscos pelo **ramal 4500** para tratamento individual.
>
> **Fonte:**
> POL-001, Seção 3.2 — Exceções, conforme Resolução ANTT nº 5.947/2021
>
> **Observação:**
> Não encontrei respaldo em documentação oficial para a possibilidade de exceção. No FAQ interno há uma orientação informal, não validada formalmente, que indica: "já houve casos em que o pessoal de Gestão de Riscos autorizou exceção — não diga que é impossível, diga que precisa de tratamento especial." *(FAQ-03, Item 3)*
> O encaminhamento correto permanece o ramal 4500, que é o canal indicado tanto pela política oficial quanto pela orientação informal.

**Problema identificado (bug v2):** FAQ-03 foi citado inline na Observação mas não aparece no campo `Fonte`. Padrão replicado nas demais respostas que usaram FAQ.

---

## Rodada 2 — SLA e tiers de clientes

---

### Pergunta 3
**Atendente:** Qual o SLA do cliente Gold?

**Resposta do assistente (v2):**
> O SLA do cliente Gold varia conforme o tipo de chamado:
>
> **Chamados gerais:** resposta em até **2 horas úteis** e resolução em até **24 horas úteis**.
>
> **Incidentes críticos:** resposta em até **30 minutos** e resolução em até **4 horas**.
>
> São considerados incidentes críticos: carga com valor acima de R$ 100.000 com status desconhecido há mais de 6h; carga perigosa com irregularidade; mais de 5 chamados do mesmo cliente em 24h sobre o mesmo problema; ou qualquer risco à segurança de pessoas.
>
> **Fonte:**
> - SLA-2024, Seção 2 — Tabela de SLAs (chamados gerais)
> - SLA-2024, Seção 2 — Tabela de SLAs (incidentes críticos)
> - SLA-2024, Seção 3 — Definição de incidente crítico
>
> **Observação:**
> A pergunta não especificou o tipo de chamado. A resposta cobre ambos os cenários previstos nos chunks. Para aplicar o SLA correto, é necessário identificar se o caso se enquadra como incidente crítico conforme os critérios da Seção 3.

---

### Pergunta 4
**Atendente:** Qual o SLA do cliente Platinum?

**Resposta do assistente (v2):**
> O tier Platinum **não existe na NovaTech**. A empresa classifica seus clientes em apenas 3 tiers: **Gold**, **Silver** e **Standard**. Não há outros tiers além desses três.
>
> Portanto, não há SLA definido para "Platinum" — a categoria simplesmente não existe na política vigente.
>
> **Fonte:**
> SLA-2024, Seção 1 — Classificação de clientes
>
> **Observação:**
> Não encontrei respaldo em documentação oficial para a existência do tier Platinum. No FAQ interno há uma orientação informal, não validada formalmente, que indica: o cliente pode estar confundindo com outra transportadora ou com um programa de fidelidade antigo descontinuado em 2022. A recomendação é orientar o cliente sobre os tiers vigentes e solicitar o número do contrato para verificação. *(FAQ-15, Item 15)*

**Problema identificado (bug v2):** FAQ-15 citado inline na Observação mas ausente no campo `Fonte`.

---

## Rodada 3 — Frete especial e cálculos

---

### Pergunta 5
**Atendente:** Frete para 600kg para Manaus?

**Resposta do assistente (v2):**
> Para um envio de 600 kg com destino a Manaus (região Norte), aplica-se a fórmula de frete especial:
>
> **Valor do frete = Valor base × Multiplicador regional × Fator de peso**
>
> Os fatores identificados nos chunks para este caso são:
> - **Fator de peso:** 1,0 (faixa de 500–1.000 kg)
> - **Multiplicador regional Norte:** 1,8
>
> Para chamados novos a partir de 01/12/2023, aplicam-se os valores da PROC-042 v2, conforme regra de transição explícita. O cálculo final **não pode ser realizado** pois o **Valor base** não está presente nos chunks disponíveis. Com os fatores acima: `Valor base × 1,8 × 1,0 = Valor base × 1,8`.
>
> **Fonte:**
> - PROC-042v2, Seção 2 — Fórmula atualizada (nov/2023)
> - PROC-042v2, Seção 2.1 — Multiplicadores regionais atualizados
> - PROC-042v2, Seção 5 — Disposições transitórias
>
> **Observação:**
> Existem duas versões da PROC-042 com multiplicadores diferentes para a região Norte (v1: 1,6 / v2: 1,8). O conflito é resolvido pela regra de transição da Seção 5: chamados abertos a partir de 01/12/2023 usam obrigatoriamente a v2. Para chamados em processamento abertos antes dessa data, aplica-se a v1. Verificar a data de abertura do chamado antes de aplicar o multiplicador.

---

### Pergunta 6
**Atendente:** Frete para 300kg para Salvador?

**Resposta do assistente (v2):**
> Não encontrei informação suficiente na documentação disponível para responder com segurança.
>
> Os chunks disponíveis cobrem apenas o **frete especial**, que se aplica a cargas **acima de 500 kg** (PROC-042). Um envio de 300 kg para Salvador (Nordeste) está abaixo desse limite e, portanto, a fórmula da PROC-042 não se aplica. Não há chunk disponível que trate do cálculo de frete para essa faixa de peso.
>
> **Fonte:**
> PROC-042v2, Seção 2 — Fórmula atualizada: "Frete especial para cargas acima de 500 kg"
>
> **Observação:**
> Recomendo escalar este caso para o supervisor ou para a área de Precificação/Comercial, que poderá informar a tabela aplicável ao frete padrão ou fracionado para essa faixa de peso.

---

### Pergunta 7
**Atendente:** Qual o multiplicador para o Sudeste?

**Resposta do assistente (v2):**
> Há dois valores vigentes para o multiplicador regional do Sudeste, dependendo da data de abertura do chamado:
>
> - **PROC-042 v1:** multiplicador **1,0**
> - **PROC-042 v2 (nov/2023):** multiplicador **1,1**
>
> A regra de transição determina: chamados abertos a partir de **01/12/2023** devem usar obrigatoriamente a v2 (multiplicador 1,1). Chamados abertos antes dessa data que ainda estejam em processamento devem usar a v1 (multiplicador 1,0).
>
> **Fonte:**
> - PROC-042, Seção 2.1 — Multiplicadores regionais (v1)
> - PROC-042v2, Seção 2.1 — Multiplicadores regionais atualizados (nov/2023)
> - PROC-042v2, Seção 5 — Disposições transitórias
>
> **Observação:**
> O multiplicador aplicável depende da data de abertura do chamado. Verificar essa informação antes de calcular o frete.

---

## Rodada 4 — Fontes informais e ausência de documentação

---

### Pergunta 8
**Atendente:** O que acontece com carga danificada?

**Resposta do assistente (v2):**
> A documentação oficial disponível trata carga danificada em trânsito (avaria) apenas sob a perspectiva de custo: quando o dano é causado pela NovaTech, a devolução é **isenta de custo para o cliente**.
>
> Não há nos chunks oficiais um procedimento detalhado específico para carga danificada — os documentos formais cobrem devolução padrão, mas não o fluxo de sinistro por avaria.
>
> **Fonte:**
> POL-001, Seção 3.5 — Custos
>
> **Observação:**
> Não encontrei respaldo em documentação oficial para o procedimento completo de carga danificada. No FAQ interno há uma orientação informal, não validada formalmente, que indica: o processo é diferente da devolução padrão — o cliente deve registrar a ocorrência em até **48 horas** após o recebimento, com fotos e laudo se possível; a NovaTech investiga e, se comprovada sua responsabilidade, reembolsa integralmente; o caso passa pelo Jurídico e deve ser encaminhado para **sinistros@novatech.com.br**. *(FAQ-38, Item 38)*
> Recomendo confirmar esse procedimento com a área de Sinistros ou supervisor antes de repassar ao cliente.

**Problema identificado (bug v2):** FAQ-38 citado inline na Observação mas ausente no campo `Fonte`.

---

### Pergunta 9
**Atendente:** Carga perigosa com frete expresso?

**Resposta do assistente (v2):**
> Não encontrei respaldo em documentação oficial para o uso de frete expresso com carga perigosa. Os chunks formais disponíveis tratam carga perigosa apenas no contexto de devolução (POL-001-B) e de incidentes críticos (SLA-2024-D), mas não há procedimento oficial que cubra especificamente a combinação de frete expresso com carga perigosa.
>
> **Fonte:**
> Não aplicável — ausência de documentação oficial sobre o tema nos chunks disponíveis.
>
> **Observação:**
> No FAQ interno há uma orientação informal, não validada formalmente, que indica: é possível, mas exige **autorização do Compliance** e **documentação ANTT atualizada**. Na prática, a autorização leva cerca de 2 dias para ser obtida, o que compromete o caráter "expresso" do serviço. A recomendação é avisar o cliente sobre esse prazo adicional. *(FAQ-32, Item 32)*
> Recomendo confirmar viabilidade e procedimento com a área de Compliance antes de oferecer essa opção ao cliente.

**Problema identificado (bug v2):** FAQ-32 foi a única fonte usada, mas o campo `Fonte` foi marcado como "Não aplicável" em vez de listar o FAQ com rótulo informal.

---

## Rodada 5 — Pergunta multi-aspecto

---

### Pergunta 10a — Resposta com prompt-v2 (com bug identificado)
**Atendente:** Prazo de devolução + carga perigosa + frete especial

**Resposta do assistente (v2):**
> **1. Prazo de devolução**
> O prazo para solicitação de devolução é de **7 dias úteis** contados a partir da data de recebimento confirmada no sistema de tracking, excluindo sábados, domingos e feriados nacionais.
> *Fonte: POL-001, Seção 3.1*
>
> **2. Carga perigosa**
> Cargas perigosas das classes 1 a 6 da ANTT **não são elegíveis para devolução pelo processo padrão**. O cliente deve contatar o setor de Gestão de Riscos pelo **ramal 4500** para tratamento individual.
> *Fonte: POL-001, Seção 3.2 — Exceções, conforme Resolução ANTT nº 5.947/2021*
>
> **3. Frete especial**
> Aplica-se a cargas **acima de 500 kg**. Fórmula: `Valor do frete = Valor base × Multiplicador regional × Fator de peso`. Fatores de peso (v2): 1,0 (500–1.000 kg) / 1,15 (1.001–3.000 kg) / 1,40 (acima de 3.000 kg). Valor base ausente nos chunks — cálculo final não pode ser realizado.
> *Fonte: PROC-042v2, Seções 2, 2.1 e 5; PROC-042, Seções 2 e 2.1*
>
> **Observação geral:**
> A pergunta não especificou se os três tópicos compõem um único cenário. Se for o caso — devolução de carga perigosa via frete especial —, o ponto determinante é o item 2: carga perigosa não segue nenhum processo padrão e deve ser tratada individualmente pelo ramal 4500.

**Problemas identificados (bug v2):**
1. FAQ-03 influenciou o tom e framing da Observação mas não foi citado em nenhum campo.
2. A afirmação "carga perigosa não segue nenhum processo padrão — nem de devolução, nem de frete especial convencional" é uma inferência que combina POL-001-B com o escopo do PROC-042, sem ser rotulada como tal.

---

### Pergunta 10b — Re-resposta com prompt-v3 (corrigida)
**Atendente:** Prazo de devolução + carga perigosa + frete especial

**Resposta do assistente (v3):**
> **1. Prazo de devolução**
> O prazo para solicitação de devolução é de **7 dias úteis** contados a partir da data de recebimento confirmada no sistema de tracking, excluindo sábados, domingos e feriados nacionais.
>
> *Fonte: POL-001, Seção 3.1 — Prazo geral*
>
> ---
>
> **2. Carga perigosa (devolução)**
> Cargas perigosas das classes 1 a 6 da ANTT não são elegíveis para devolução pelo processo padrão, independentemente do prazo. O cliente deve contatar o setor de Gestão de Riscos pelo **ramal 4500** para tratamento individual.
>
> *Fonte:*
> - POL-001, Seção 3.2 — Exceções, conforme Resolução ANTT nº 5.947/2021
> - FAQ Atendimento, Item 3 — Devolução de carga perigosa *(fonte informal, não validada formalmente)*
>
> *Observação:* O documento oficial veda o processo padrão, mas não declara a devolução impossível em todos os cenários. No FAQ interno há uma orientação informal, não validada formalmente, que indica que o setor de Gestão de Riscos já autorizou exceções — e que não se deve dizer ao cliente que é impossível, mas sim que requer tratamento especial.
>
> ---
>
> **3. Frete especial**
> Aplica-se a cargas acima de 500 kg. Fórmula vigente: `Valor do frete = Valor base × Multiplicador regional × Fator de peso`. Fatores de peso (v2, para chamados a partir de 01/12/2023): 1,0 (500–1.000 kg) / 1,15 (1.001–3.000 kg) / 1,40 (acima de 3.000 kg). O Valor base não está presente nos chunks — cálculo final não pode ser realizado sem essa informação.
>
> *Fonte:*
> - PROC-042v2, Seção 2 — Fórmula atualizada (nov/2023)
> - PROC-042v2, Seção 2.1 — Multiplicadores regionais atualizados
> - PROC-042v2, Seção 5 — Disposições transitórias
> - PROC-042, Seções 2 e 2.1 — versão original (referência para chamados anteriores a 01/12/2023)
>
> ---
>
> **Observação geral:**
> A pergunta não especificou se os três tópicos compõem um único cenário. Se for o caso — devolução de carga perigosa via frete especial — o ponto determinante é o item 2: POL-001-B veda o processo padrão de devolução para carga perigosa. *Inferência com base em POL-001-B e PROC-042v2-A:* como o frete especial (PROC-042) trata de transporte, não de devolução, e a POL-001-B exige tratamento individual pelo ramal 4500, a combinação dos dois processos precisaria de validação pela Gestão de Riscos antes de qualquer cálculo de frete reverso.

---

## Observações gerais da sessão

- O prompt-v2 seguiu corretamente a estrutura **Resposta / Fonte / Observação** em todas as interações.
- A distinção entre fonte oficial e FAQ informal foi aplicada consistentemente no corpo das respostas — o bug estava na ausência de listagem das fontes informais no campo `Fonte`.
- A limitação por falta de dado (valor base do frete) foi corretamente sinalizada nas Perguntas 5 e 6 sem invenção de valor.
- A exceção de carga perigosa foi incluída proativamente mesmo em perguntas genéricas (Pergunta 1).
- Fonte "Não aplicável" foi usada indevidamente na Pergunta 9 — quando a única resposta vem de fonte informal, ela deve ser listada em `Fonte` com o rótulo adequado, não omitida.
- **Bug sistêmico identificado (v2 → v3):** toda fonte usada na Observação (inclusive FAQ) deve aparecer no campo `Fonte`. A regra da v2 não tornava isso explícito. Corrigido no prompt-v3.
- **Bug adicional identificado:** inferências que combinam informações de chunks distintos sem trecho direto de suporte não estavam sendo rotuladas. Regra adicionada na v3.
