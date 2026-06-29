# Exercício 3.2 — Revisão crítica de código gerado por IA
**Papel:** Desenvolvedor  
**Tópico:** Revisão Crítica de Outputs de IA  
**Data:** 2026-06-29

## Revisão humana, sem uso de ferramentas
Revisão inicial antes de utilizar Claude/Copilot.

### Problemas encontrados

#### 1 - Uso de "any" como type:

```typescript
const body = await request.json() as any;
```
**Tipo**: violação do AGENTS.md  
O uso de um tipo genérico em um linguagem como TypeScript é contra-intuitivo e não aproveita os recursos da linguagem.

#### 2 - Nada está sendo validado no request body

```typescript
const feedback = {
    queryId: body.queryId,
    rating: body.rating,
    comment: body.comment,
    attendantEmail: body.attendantEmail,
    timestamp: new Date().toISOString()
  };
```
**Tipo**: violação do AGENTS.md  
Qualquer dado por ser aceito, algo que vai contra os princípios definidos no projeto. Uso de schema Zod evitaria o problema

#### 3 - Cosmos sendo iniciado dentro da função
```typescript
const { CosmosClient } = require('@azure/cosmos');
const client = new CosmosClient(process.env.COSMOS_CONNECTION_STRING);
```
**Tipo**: violação do AGENTS.md  
Quando o client do Cosmos é iniciado dentro da função, sempre que a função por chamada o client sera criaod, gerando um overload por criar multiplas versões do client e não reaproveitar uma instância única

#### 4 - Não existe nenhum tratamento de erro
**Tipo**: bug potencial  
Não há especificidade de erros acontecendo, tudo resulta em um erro 500 para o usuário. Uso de tipos específicos é o ideal.

#### 5 - Resposta como string simples, sem tipo
**Tipo**: violação do AGENTS.md
```typescript
return { status: 200, body: 'OK' };
```

Como citado no item 1, o uso de um tipo genérico em um linguagem como TypeScript é contra-intuitivo e não aproveita os recursos da linguagem. Um retorno em formato JSON seria uma melhor opção.


#### 6 - Problema de logs

```typescript
console.log(JSON.stringify(feedback));
```
**Tipo**: violação do AGENTS.md, falha de segurança    

O uso de console.log é desaprovado pelo AGENTS.md, e o log direto, sem tratamento, permite o vazamento de dados.

#### 7 - Mistura de import e require

```typescript
import { app, HttpRequest, HttpResponseInit } from '@azure/functions';

...

  const { CosmosClient } = require('@azure/cosmos');
```
**Tipo**: violação do AGENTS.md    

O uso de require dinâmico é  desaprovado pelo AGENTS.md.