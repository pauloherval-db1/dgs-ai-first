# Log de Sessão de Teste — Assistente NovaTech
**Data:** 2026-05-28  
**Prompt testado:** prompt-v1.md  
**Chunks utilizados:** Anexo B (chunks completos — POL-001, PROC-042, PROC-042-v2, SLA-2024, FAQ-Atendimento)

---

## Rodada 1 — Chunks iniciais simples (A, B, C)

> Estes três primeiros testes foram realizados com um conjunto reduzido de chunks (versão simplificada antes da substituição pelo Anexo B completo).

---

### Pergunta 1
**Atendente:** Qual o prazo de devolução para carga perigosa?

**Resposta do assistente:**
> Cargas classificadas como perigosas (classes 1 a 6 da ANTT) **não estão cobertas** pela política de devolução. A POL-001 estabelece o prazo de 7 dias úteis para devoluções, porém esse prazo aplica-se exclusivamente a mercadorias que não sejam cargas perigosas — estas constam explicitamente como exceção à regra geral.
>
> **Fonte:** Política de Devolução POL-001, seção 3.2.
>
> **Observação:** A documentação disponível não prevê prazo alternativo de devolução para cargas perigosas — elas estão excluídas da política, não contempladas com prazo diferenciado. Caso o atendente precise orientar o cliente sobre como proceder com esse tipo de carga, recomenda-se escalar para o supervisor ou área responsável, pois não há informação suficiente nos chunks disponíveis para cobrir esse cenário.

---

### Pergunta 2
**Atendente:** Meu cliente é Gold, qual o SLA de resolução?

**Resposta do assistente:**
> Para clientes Gold, o SLA de resolução é de **até 24 horas**, com tempo de resposta inicial de até 2 horas.
>
> **Fonte:** Tabela SLA-2024.

---

### Pergunta 3
**Atendente:** Quanto custa o frete para 600kg para Manaus?

**Resposta do assistente:**
> Por tratar-se de carga acima de 500 kg com destino a Manaus (Região Norte), aplica-se o frete especial com a seguinte fórmula:
>
> **valor base × 1,8**
>
> O valor final depende do valor base, que não consta nos chunks fornecidos. Não é possível calcular o custo total sem essa informação.
>
> **Fonte:** PROC-042-v2, seção 2.
>
> **Observação:** O chunk não informa como o valor base é determinado. Para obter o valor final, consulte a tabela de valor base ou acione a área responsável pelo cálculo de frete.

---

## Rodada 2 — Chunks completos do Anexo B

---

### Pergunta 4
**Atendente:** Qual o prazo de devolução?

**Resposta do assistente:**
> O prazo de devolução é de **até 7 dias úteis** após o recebimento da mercadoria. Para solicitar a devolução, o cliente deve abrir um chamado no portal e anexar fotos da mercadoria.
>
> Há uma exceção relevante: **cargas perigosas das classes 1 a 6 da ANTT não podem ser devolvidas** por essa política.
>
> **Fonte:** Política de Devolução POL-001, seção 3.2.

---

### Pergunta 5
**Atendente:** Qual o prazo de devolução? *(refeita com chunks completos)*

**Resposta do assistente:**
> O prazo para solicitar devolução é de **até 7 dias úteis** após a data de recebimento confirmada no sistema de tracking. A contagem exclui sábados, domingos e feriados nacionais. Solicitações após esse prazo não são elegíveis para devolução padrão e devem ser encaminhadas ao Comercial.
>
> **Fonte:** POL-001, Seção 3.1 (prazo geral) e Seção 3.5 (prazo expirado).
>
> **Observação:** Cargas perigosas das classes 1 a 6 da ANTT **não são elegíveis** para devolução pelo processo padrão, independentemente do prazo. Nesses casos, o cliente deve contatar o setor de Gestão de Riscos pelo ramal 4500 para tratamento individual (POL-001, Seção 3.2).

---

### Pergunta 6
**Atendente:** Posso devolver carga perigosa?

**Resposta do assistente:**
> Cargas perigosas classificadas nas classes 1 a 6 da ANTT **não são elegíveis para devolução pelo processo padrão**. Isso inclui explosivos (classe 1), gases (classe 2), líquidos inflamáveis (classe 3), sólidos inflamáveis (classe 4), oxidantes e peróxidos (classe 5), e substâncias tóxicas e infectantes (classe 6). O cliente deve entrar em contato com o setor de **Gestão de Riscos pelo ramal 4500** para tratamento individual.
>
> **Fonte:** POL-001, Seção 3.2 (Exceções), conforme Resolução ANTT nº 5.947/2021.
>
> **Observação:** O FAQ interno (FAQ-03) menciona que o setor de Gestão de Riscos já autorizou exceções em casos anteriores. No entanto, trata-se de orientação informal, não validada formalmente — não deve ser apresentada ao cliente como regra. A documentação oficial (POL-001) não prevê prazo nem procedimento alternativo de devolução para cargas perigosas além do encaminhamento ao ramal 4500.

---

## Observações gerais da sessão

- O prompt seguiu corretamente a estrutura **Resposta / Fonte / Observação** em todas as interações.
- A distinção entre fonte oficial e FAQ informal foi aplicada adequadamente na Pergunta 6.
- A limitação por falta de dado (valor base do frete) foi corretamente sinalizada na Pergunta 3 sem invenção de valor.
- A exceção de carga perigosa foi incluída proativamente mesmo em perguntas genéricas sobre prazo de devolução.
