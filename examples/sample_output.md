# Exemplo de saída (execução real com LLM)

Trecho ilustrativo do que o terminal costuma mostrar após `python -m app.main --demo` com `OPENAI_API_KEY` configurada. O texto exato varia conforme o modelo e a versão dos documentos em `data/`.

## Logs resumidos

```text
Iniciando servidor MCP em subprocess (stdio)...
Conectado ao MCP. Executando fluxo do agente...

Passo 1: entendimento da história (LLM)...
  Resumo para busca: O cliente deseja atualizar dados cadastrais para manter o perfil correto.
Passo 2: recuperando contexto com RAG via MCP...
Using MCP tool: search_knowledge_base
  Contexto RAG recuperado.
Passo 3: consultando memória (análises anteriores) via MCP...
Using MCP tool: list_previous_analyses
Passo 4: avaliação e geração estruturada (LangChain + LLM)...
Passo 5: persistindo análise na memória local via MCP...
Using MCP tool: save_story_analysis
  Memória atualizada (memory/history.json).
```

## Resultado (markdown no terminal)

```markdown
## Resultado da análise

**Diagnóstico:** A história está no formato clássico, mas ainda é genérica: não define quais dados, quais regras de validação, nem o valor entregue ao negócio além de “cadastro atualizado”.

### Problemas / lacunas

- Persona “cliente” sem contexto (autenticado? qual perfil?).
- Verbo “alterar dados” sem limites de escopo (LGPD, campos sensíveis, auditoria).
- Ausência de critérios de aceite observáveis.

### Perguntas para o refinamento

- Quais campos são editáveis neste incremento?
- Quais validações são obrigatórias (formato, unicidade, consistência com pedidos)?
- O que deve acontecer após salvar (notificação, reprocessamento, log de auditoria)?

### Critérios de aceite sugeridos

- Dado um cliente autenticado, ao acessar “Meu perfil”, ele visualiza apenas os campos permitidos para edição.
- Dado um envio com dados inválidos, o sistema impede o salvamento e exibe mensagens específicas por campo.
- Dado um salvamento bem-sucedido, o sistema confirma visualmente e persiste os dados no backend.

### Riscos

- Escopo crescer implicitamente para “qualquer alteração cadastral”.
- Impacto em compliance se campos sensíveis forem tratados sem trilha adequada.

### Dependências

- Serviço de autenticação e modelo de dados do cadastro.
- Contrato da API de perfil/cliente.

### História refinada

Como cliente autenticado, quero editar no meu perfil os campos permitidos (por exemplo, telefone e endereço) com validações claras, para que minhas entregas e comunicações usem informações corretas e atualizadas.

### Notas de confiança / incertezas

- Não há menção a estados de erro, campos específicos nem integrações; as sugestões assumem um fluxo típico de “perfil de e-commerce”.
```

## Modo `--dry-run`

Com `python -m app.main --demo --dry-run`, a saída segue a mesma estrutura de seções, mas o diagnóstico inclui a marca `[DRY-RUN]` e as notas deixam claro que não houve chamadas à OpenAI nem ao MCP.
