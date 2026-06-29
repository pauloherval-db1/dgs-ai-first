# Exercício 3.2 — Comparativo: revisão humana vs. revisão por Claude
**Data:** 2026-06-29

---

## Tabela comparativa de achados

| # | Problema | Humano | Claude | Observação |
|---|---|:---:|:---:|---|
| 1 | Arquivo no lugar errado | — | ✓ | Só o Claude identificou |
| 2 | `as any` + sem validação de tipo | ✓ | ✓ | Ambos encontraram |
| 3 | Ausência de schema Zod | ✓ | ✓ | Ambos encontraram |
| 4 | `CosmosClient` instanciado por request | ✓ | ✓ | Ambos encontraram; Claude foi mais fundo |
| 5 | Sem tratamento de erro | ✓ | ✓ | Ambos encontraram |
| 6 | Retorno sem tipo (`body: 'OK'`) | ✓ | — | Só o humano identificou |
| 7 | `console.log` + vazamento de PII | ✓ | ✓ | Ambos encontraram; Claude foi mais específico |
| 8 | `require()` em ESM quebra em runtime | parcial | ✓ | Humano viu como violação de estilo; Claude identificou o erro de runtime |

**Total de achados únicos — Humano:** 2 (itens 6 e 8 parcial)  
**Total de achados únicos — Claude:** 2 (itens 1 e 8 aprofundado)  
**Achados em comum:** 5

---

## Análise qualitativa

### O que o humano fez melhor

**Item 5 — Retorno sem tipo (`body: 'OK'`):** o humano notou que a resposta deveria ser um objeto JSON tipado em vez de uma string simples. Claude não sinalizou esse ponto, focando apenas em problemas bloqueadores de runtime e segurança.

**Sensibilidade ao contexto TypeScript:** o humano identificou o `as any` como um problema de linguagem ("contra-intuitivo em TypeScript"), conectando diretamente à filosofia da linguagem. Claude fez o mesmo, mas de forma mais técnica e menos contextualizada para o time.

---

### O que o Claude fez melhor

**Item 1 — Arquivo no lugar errado:** Claude verificou a estrutura real do repositório (`/src/functions/query/handler.ts`, `/src/functions/health/handler.ts`) antes de apontar o desvio. O humano não cruzou a localização do arquivo com a convenção existente.

**Item 8 — `require()` em ESM:** o humano classificou corretamente como violação do AGENTS.md (mistura de import/require). Claude foi além: verificou o `package.json`, encontrou `"type": "module"` e concluiu que o `require` lança `ReferenceError` em runtime — não é apenas estilo, é um erro garantido. Essa distinção muda a severidade do item de "violação de padrão" para "bloqueador de runtime".

**Item 7 — Log de PII:** ambos identificaram o `console.log`, mas Claude especificou que `attendantEmail` é o campo sensível exposto, mencionou o risco de exposição no Application Insights e apontou `pino` como a alternativa correta já estabelecida no projeto — informação que encontrou no stub do `query/handler.ts`.

**Estrutura de severidade:** Claude classificou cada item com "Bloqueia merge?" explícito, o que facilita a triagem pelo Tech Lead. A revisão humana não distinguiu severidade entre os itens.

---

### O que ambos fizeram bem

- Identificaram os dois problemas mais críticos (PII em log e ausência de Zod) sem precisar de prompt adicional.
- Conectaram os problemas ao AGENTS.md do projeto, não apenas a boas práticas genéricas.
- Chegaram ao mesmo veredito: o código não deve ser mergeado.

---

## Conclusão

As duas revisões são complementares. O humano detectou um problema que o Claude perdeu (retorno sem tipo) e trouxe uma perspectiva contextual sobre a linguagem. O Claude foi mais sistemático na verificação de contexto (leu o `package.json`, a estrutura de diretórios, os handlers de referência) e transformou um achado de estilo em um bloqueador de runtime.

Na prática, a combinação das duas revisões produz cobertura mais completa do que qualquer uma isolada — o que é exatamente o ponto do exercício.
