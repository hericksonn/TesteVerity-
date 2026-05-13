# Agile Story Assistant

MVP em Python: um agente que apoia **Product Owners** e **Scrum Masters** no **refinamento de histórias de usuário**. Ele aponta ambiguidades, sugere critérios de aceite, levanta riscos e perguntas para o refinamento e propõe uma versão reescrita da história, usando **RAG** com documentos locais (DoR, DoD, guia), **memória** em JSON, **MCP** com ferramentas reais e **orquestração** em etapas no código.

## Problema

Histórias costumam chegar ao refinamento ainda vagas: escopo difuso, critérios de aceite incompletos ou dependências que só aparecem no meio da sprint. Isso gera retrabalho e dificulta estimativa.

A proposta aqui é dar uma **leitura estruturada** antes da conversa do time — não substituir PO, SM nem desenvolvimento.

## Fluxo do agente

1. Resumo curto da história (para orientar a busca).
2. **RAG via MCP**: trechos relevantes de `data/*.md`.
3. **Memória via MCP**: análises anteriores em `memory/history.json`.
4. **Análise estruturada** com LangChain + API OpenAI (JSON com campos fixos).
5. **Persistência via MCP** da análise no histórico.

O terminal imprime linhas como `Using MCP tool: search_knowledge_base` para facilitar a demonstração em vídeo.

## Ambiente recomendado

- **Python 3.11+**
- Conta OpenAI com chave de API (chat + embeddings) para a execução completa.

## Como executar

Na **raiz** do repositório (onde estão `app/`, `data/`, `memory/`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Preencha OPENAI_API_KEY no .env para execução real.
```

### Execução com LLM e MCP (entrega principal)

```powershell
python -m app.main --demo
python -m app.main --story-file examples\sample_story.txt
python -m app.main
```

No modo interativo, finalize com uma linha contendo apenas `---`.

### Modo `--dry-run` (sem OpenAI, sem MCP)

Útil para quem for avaliar o fluxo **sem chave** e **sem custo de API**:

```powershell
python -m app.main --demo --dry-run
```

Neste modo: lê os `.md` de `data/`, monta um contexto estático (sem embeddings), gera uma análise **simulada** e grava em `memory/history.json` diretamente pelo `MemoryStore`. As linhas `Using MCP tool: … (dry-run — não invocado)` deixam explícito que o protocolo MCP não foi usado nessa execução.

A demonstração em vídeo do desafio deve priorizar a execução **com** API e MCP.

### Testes

```powershell
pytest
```

Testes cobrem `MemoryStore`, carregamento de Markdown e formatação da saída — **sem** chamar LLM.

### Servidor MCP isolado

```powershell
python -m app.mcp.server
```

## Estrutura do código

| Caminho | Função |
|--------|--------|
| `app/main.py` | CLI; modo real sobe MCP em subprocess (stdio). |
| `app/agents/story_refinement_agent.py` | Orquestração com MCP + validação básica dos retornos das ferramentas. |
| `app/agents/dry_run.py` | Fluxo local sem API/MCP. |
| `app/prompts/story_prompts.py` | Prompts e formato JSON esperado. |
| `app/rag/` | Carga de Markdown, chunks, embeddings OpenAI, cosseno. |
| `app/memory/memory_store.py` | Histórico em `memory/history.json`. |
| `app/mcp/server.py` | Ferramentas MCP: `search_knowledge_base`, `save_story_analysis`, `list_previous_analyses`. |
| `app/services/llm_service.py` | LangChain (`ChatOpenAI`) para resumo e análise. |
| `data/` | Base documental do RAG. |

## Decisões técnicas

Optei por manter o MVP simples e fácil de executar localmente. A aplicação foi construída em **Python** pela facilidade de integração com APIs de LLM, embeddings e protocolos como o MCP.

Usei a **OpenAI** para chat e embeddings, com modelos configuráveis por variáveis de ambiente. Os **prompts** ficaram em módulo separado para facilitar revisão e ajustes sem misturar com a orquestração.

O **RAG** foi implementado sobre arquivos **Markdown** locais, simulando uma base de conhecimento da squad (Definition of Ready, Definition of Done, guia de histórias). Para o tamanho deste MVP, **fragmentação + embeddings + similaridade por cosseno** é suficiente e evita dependência de banco ou serviço vetorial externo.

A **memória** foi mantida em **JSON** local para registrar análises anteriores sem infra extra. Em produção, isso poderia migrar para banco relacional ou vetorial, com políticas de retenção e privacidade.

O **MCP** expõe ferramentas de forma padronizada (`search_knowledge_base`, `list_previous_analyses`, `save_story_analysis`). A CLI atua como **cliente MCP** e sobe o servidor via **stdio**, padrão comum em integrações com IDEs e clientes compatíveis. A mesma ideia poderia evoluir para ferramentas que chamam Jira, Azure DevOps ou Confluence.

A **orquestração** multi-step ficou explícita no agente (passos numerados e logs), em vez de esconder tudo dentro de um único prompt monolítico.

## Como o RAG foi usado

Antes da análise final, o agente recupera trechos dos documentos em `data/` com base na história e em um resumo curto. Assim a resposta fica ancorada no que a squad definiu como DoR, DoD e boas práticas de escrita — e não só no conhecimento genérico do modelo.

## Como a memória foi implementada

O arquivo `memory/history.json` guarda cada análise (história, resumo, campos principais, timestamp). Na execução real, leitura e gravação passam pelas ferramentas MCP; no `--dry-run`, a gravação é direta pelo `MemoryStore`, apenas para permitir validação offline.

## Como o MCP foi usado

Três ferramentas no servidor (`app/mcp/server.py`):

- **search_knowledge_base**: consulta a base em `data/` (com embeddings no subprocess).
- **list_previous_analyses**: devolve texto com entradas recentes do histórico.
- **save_story_analysis**: persiste um registro JSON no histórico.

O cliente valida `isError` e mensagens de erro textuais; se a busca falhar, o agente segue com um contexto RAG mínimo explícito no prompt. Se o salvamento não puder ser confirmado, o log deixa isso claro em vez de assumir sucesso.

## Prompts

Definidos em `app/prompts/story_prompts.py`: saída de análise em **JSON** com chaves fixas (`diagnosis`, `issues`, `refinement_questions`, `acceptance_criteria`, `risks`, `dependencies`, `refined_user_story`, `confidence_notes`) e um prompt separado para o **resumo** usado na busca.

## Exemplo de saída

Um exemplo editado de logs e markdown está em [`examples/sample_output.md`](examples/sample_output.md) (sem chaves nem dados sensíveis).

## Métricas de impacto

Indicadores úteis para medir efeito na squad, combinando números e percepção:

- Histórias devolvidas por falta de clareza (por sprint).
- Dúvidas de escopo durante a sprint (retrospectiva).
- Percentual de histórias com critérios de aceite completos ao entrar na sprint.
- Retrabalho por entendimento incorreto (bugs/reopens categorizados).
- Tempo médio do PO/SM preparando histórias (amostra simples já ajuda).
- Pesquisa curta com o time sobre qualidade do refinamento.

## Possíveis evoluções

- Integração com **Jira** ou **Azure DevOps** (ler issue, postar comentário com a análise).
- Base vetorial persistente para documentos maiores.
- Etapa de **aprovação humana** antes de salvar ou publicar sugestões.
- Métricas históricas de qualidade do backlog por sprint.

## Variáveis de ambiente

Ver `.env.example`. Para execução real:

- `OPENAI_API_KEY` (obrigatória)
- `OPENAI_MODEL` (padrão `gpt-4o-mini`)
- `OPENAI_EMBEDDING_MODEL` (padrão `text-embedding-3-small`)

## Limitações

Este projeto é um MVP: base pequena e local, memória em arquivo, validação de negócio continua com o time. O agente organiza pontos para discussão; quem decide é a squad.

## Comandos para testar

Na raiz do repositório, com o ambiente virtual ativo e dependências instalados (veja a seção **Como executar**).

**Testes automatizados:**

```powershell
pytest
```

**Execução com LLM e MCP** (requer `OPENAI_API_KEY` no `.env`):

```powershell
python -m app.main --demo
```

**Conteúdo salvo em memória** (no PowerShell, use UTF-8 para acentos corretos no terminal):

```powershell
Get-Content memory\history.json -Encoding utf8
```

**Execução sem API** (resposta simulada; não sobe subprocess MCP):

```powershell
python -m app.main --demo --dry-run
```

**Servidor MCP sozinho** (stdio; encerre com Ctrl+C quando não precisar mais):

```powershell
python -m app.mcp.server
```

## Licença

Uso educacional / portfólio para o teste técnico, salvo indicação em contrário pelo autor.
