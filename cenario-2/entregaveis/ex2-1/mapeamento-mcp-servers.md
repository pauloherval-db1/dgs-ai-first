# Mapeamento MCP Servers — NovaTech Assistant

> **ADRs relacionados:**
> - [ADR 0001](../Anexo-D-starter-repo-novatech-assistant/novatech-assistant/docs/adr/0001-stack-tecnica-rag-local-gratuita.md) — Stack técnica RAG com ferramentas locais e gratuitas
> - [ADR 0004](../Anexo-D-starter-repo-novatech-assistant/novatech-assistant/docs/adr/0004-mcp-integracao-ferramentas-dados.md) — Integração MCP para acesso a ferramentas e dados
> - [ADR 0005](../Anexo-D-starter-repo-novatech-assistant/novatech-assistant/docs/adr/0005-least-privilege-mcp-security.md) — Least privilege e segurança em MCP servers

## Necessidades do projeto × Server

| Necessidade | Server | Pasta/Escopo |
|---|---|---|
| Ler e escrever código, specs, skills, testes | `filesystem-rw` | `./src ./specs ./skills ./tests` |
| Ler documentação de negócio (Confluence simulado) | `filesystem-ro-docs` | `./docs/novatech` |
| Recuperar chunks (Azure AI Search simulado) | `filesystem-ro-docs` | `./data/retrieval-corpus` |
| Histórico, diff e branches do repositório (GitHub simulado) | `git` | `.` (raiz do repo) |
| Glossário e decisões persistentes entre sessões | `memory` | — (grafo local interno) |
| Explorar primitivas MCP (aprendizado/sandbox) | `everything` | — |

---

## Detalhamento por server

### `filesystem-rw` — código, specs, skills, testes

**Referência:** [ADR 0005 — Least privilege](../Anexo-D-starter-repo-novatech-assistant/novatech-assistant/docs/adr/0005-least-privilege-mcp-security.md)

- **Escopo:** `./src`, `./specs`, `./skills`, `./tests`
- **Tools expostos:** `read_file`, `write_file`, `create_directory`, `list_directory`, `move_file`, `search_files`
- **Quem consome:** Dev (implementação de código, geração de tasks.md, escrita de skills e specs)
- **Least privilege:** escopo restrito ao que o Dev precisa criar/modificar. `./prompts`, `./docs`, `./data`, `./infra` e `.github/` estão ausentes — o server não os enxerga. Enforcement por ausência de escopo (o mais confiável: o server não pode listar o que não está no seu escopo).

### `filesystem-ro-docs` — documentação de negócio e corpus

**Referências:** [ADR 0001](../Anexo-D-starter-repo-novatech-assistant/novatech-assistant/docs/adr/0001-stack-tecnica-rag-local-gratuita.md), [ADR 0003](../Anexo-D-starter-repo-novatech-assistant/novatech-assistant/docs/adr/0003-governanca-conflito-documental.md), [ADR 0005](../Anexo-D-starter-repo-novatech-assistant/novatech-assistant/docs/adr/0005-least-privilege-mcp-security.md)

- **Escopo:** `./docs/novatech`, `./data/retrieval-corpus`
- **Tools expostos:** `read_file`, `list_directory`, `search_files` (o server expõe write, mas o enforcement real é via permissões de SO)
- **Quem consome:** Product Specialist (requisitos), Tech Lead (plano técnico), agente RAG (recuperação de chunks simulada)
- **Least privilege:** separado do escopo rw por instância própria. Enforcement aplicado por permissões de SO (`chmod -R 555 docs/novatech data/retrieval-corpus`), de modo que o servidor mantém apenas leitura efetiva sobre as fontes de negócio.

### `filesystem-ro-prompts` — system prompt

**Referência:** [ADR 0005 — Least privilege](../Anexo-D-starter-repo-novatech-assistant/novatech-assistant/docs/adr/0005-least-privilege-mcp-security.md)

- **Escopo:** `./prompts`
- **Tools expostos:** `read_file`, `list_directory` (write presente no server, bloqueado por OS permissions)
- **Quem consome:** qualquer agente que precise ler o system prompt ou changelog — nunca escrever via MCP
- **Least privilege:** `system-prompt.md` é o único artefato cujo overwrite acidental impacta o runtime do assistente. Isolado em instância própria para que o server rw do código não o alcance. Enforcement aplicado por permissões de SO (`chmod -R 555 prompts/`).

### `git` — histórico e branches

**Referência:** [ADR 0005 — Least privilege](../Anexo-D-starter-repo-novatech-assistant/novatech-assistant/docs/adr/0005-least-privilege-mcp-security.md)

- **Escopo:** `--repository .` (raiz do repositório)
- **Tools expostos:** `git_log`, `git_diff`, `git_status`, `git_show`, `git_blame`, `git_branch` (uso esperado)
- **Quem consome:** Tech Lead (histórico ao planejar), Dev (contexto ao implementar), Code Reviewer
- **Least privilege:** o `mcp-server-git` expõe também tools de escrita (`git_commit`, `git_add`, `git_checkout`) sem filtro nativo no `mcp.json`. Controle por instrução no `AGENTS.md`: agentes não devem usar tools de escrita do git server exceto quando explicitamente instruídos.

### `memory` — glossário e decisões persistentes

- **Escopo:** grafo local interno (sem pasta)
- **Tools expostos:** `create_entities`, `create_relations`, `add_observations`, `search_nodes`, `open_nodes`
- **Quem consome:** todos os papéis — linguagem ubíqua, decisões menores entre sessões
- **Least privilege:** read/write indistintos por design do server. Risco aceito: corrupção do grafo não compromete código nem documentos.

### `everything` — exploração de primitivas MCP

- **Escopo:** sem pasta — server de referência do protocolo
- **Tools expostos:** exemplos de tools, resources e prompts do protocolo MCP
- **Quem consome:** Dev explorando o protocolo antes de criar servers customizados
- **Least privilege:** sem acesso a nenhuma pasta do projeto. Sem risco para artefatos reais.

---

## Estado de enforcement de least privilege por server

| Server | Enforce real | Ação pendente |
|---|---|---|
| `filesystem-rw` | Ausência de escopo protege `docs/`, `prompts/`, `infra/`, `.github/` | Nenhuma |
| `filesystem-ro-docs` | Permissões de SO aplicadas; leitura efetiva apenas | Nenhuma |
| `filesystem-ro-prompts` | Permissões de SO aplicadas; leitura efetiva apenas | Nenhuma |
| `git` | Nenhum — tools de escrita presentes no server | Documentar tools proibidas no `AGENTS.md` |
| `memory` | Nenhum — read/write por design | Nenhuma (risco aceito) |
| `everything` | Total — sem acesso a pastas do projeto | Nenhuma |

---

## Alternativas de enforcement consideradas e descartadas nesta fase

| Mecanismo | Enforcement real | Motivo de não adotar agora |
|---|---|---|
| OS permissions (`chmod`) | Total | Pendente — aplicar antes de sessões com agentes reais |
| `mcp.json` por papel (dev/tech-lead/ps) | Por configuração | Quando o projeto tiver múltiplos agentes com papéis distintos |
| Proxy MCP com filtro de tools | Total | Custo de implementação alto para fase local |
| Container com volume `:ro` | Total | Fora do escopo desta fase |

---

## Matriz de verificação do Exercício 2.1

| Critério obrigatório | Evidência no entregável | Status | Observação |
|---|---|---|---|
| Servers locais e gratuitos apenas | `mcp.json` usa `npx`, `uvx` e servers locais sem dependência paga | Atendido | Nenhum serviço externo aparece na configuração |
| Least privilege concreto | Mapeamento separa `filesystem-rw` de `filesystem-ro-docs` e `filesystem-ro-prompts` | Atendido | Escopos mínimos por necessidade |
| Doc lido via MCP | `session-export.md`, Turno 4 | Atendido | Leitura de `docs/novatech/FAQ-atendimento.md` |
| Chunk recuperado via corpus | `session-export.md`, Turnos 1 e 2 | Atendido | Respostas citam chunks do corpus de RAG |
| Histórico lido via git | `session-export.md`, Turnos 5 e 6 | Atendido | `git log` e resumo do commit inicial |
| Riscos específicos e mitigação | Seção de riscos do mapeamento | Atendido | Foco em escopo amplo, escrita sem gate e memória |
