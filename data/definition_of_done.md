# Definition of Done (DoD)

Este documento define quando uma entrega associada a uma história é considerada **concluída** pelo time.

## DoD padrão (MVP de produto)

- Código revisado (pull request aprovado) e integrado na branch principal.
- Testes automatizados relevantes passando (unitários e/ou integração conforme risco).
- Observabilidade mínima: logs ou métricas quando aplicável a incidentes comuns.
- Documentação atualizada quando há impacto em operação, contrato de API ou UX crítica.
- Feature validada pelo PO ou delegado em ambiente de homologação/staging.

## Critérios de aceite vs DoD

- **Critérios de aceite** dizem *o que* o incremento precisa cumprir para a história ser aceita.
- **DoD** diz *como* o time garante qualidade e sustentabilidade da entrega.

## Sinais comuns de “quase pronto”

- “Funciona na minha máquina”, mas não em staging.
- Testes frágeis ou ausentes em trecho com lógica de negócio relevante.
- UX inconsistente com padrões do produto sem registro de decisão.
