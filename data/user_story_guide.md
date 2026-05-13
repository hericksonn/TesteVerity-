# Guia de escrita de histórias de usuário

## Formato recomendado

Como **[persona]**, quero **[ação/capacidade]**, para **[benefício/resultado]**.

## Boas práticas

- **Persona**: quem se beneficia (usuário final, admin, parceiro, sistema interno).
- **Objetivo**: verbo no infinitivo ou ação clara, sem jargão ambíguo.
- **Benefício**: por que isso importa para o usuário ou para o negócio.
- **Critérios de aceite**: comportamento observável, dados envolvidos, estados e erros.

## Exemplos fracos vs fortes

**Fraco:** “Como cliente, quero alterar meus dados para manter meu cadastro atualizado.”

**Melhor:** “Como cliente autenticado, quero editar telefone e endereço no meu perfil, para que meus pedidos sejam entregues corretamente.”

Critérios de aceite exemplo:

- Campos editáveis: telefone e endereço; demais campos somente leitura.
- Validação de formato de telefone e endereço obrigatório.
- Mensagens de erro claras e persistência após salvar com sucesso.

## Checklist rápido

- Dá para escrever testes a partir da história sem perguntas enormes?
- O incremento cabe em um sprint (ou foi fatiado)?
- Há definição do que acontece em falhas comuns?
