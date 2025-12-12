# BACKLOG.md — Matriz de Prioridade do Projeto Maestro

Este documento consolida todas as informações de "Próximos Passos", "Backlog Técnico" e sugestões pendentes dos logs de desenvolvimento.

## 🔥 Funcionalidades Core (Must Have)

O que falta para o MVP ser completo:
- `maestro context show` — Visualização detalhada do contexto ativo
- `maestro output show` — Inspeção de saídas específicas
- `maestro session stop` — Encerramento controlado de sessões ativas
- `maestro session resume` — Retomada de sessões inativas

## 🛡️ Robustez e Segurança (High Priority)

- Tratamento de erros robusto para JSON corrompido e metadados faltantes
- Implementar validações mais rígidas e recuperação de erros
- Implementar confirmação opcional para remoção de itens do contexto
- Tratamento de Ctrl+C (Graceful exit) no comando `run`
- Timeout configurável para subprocessos
- Remover duplicação de código (usar `require_active_session()`)

## ✨ Experiência do Usuário (Medium Priority)

- Implementar spinner mais sofisticado com duração estimada e progresso
- Adicionar pré-visualização do contexto antes da execução
- Melhorar formatação da saída para suportar Markdown no terminal
- Feedback visual de envio de contexto
- Streaming de resposta em tempo real
- Flags (`--verbose`, `--compact`, `--json`), paginação, filtragem por tipo
- Ordenação personalizada, data/hora de adição
- Busca textual, agrupamento por tipo/origem
- Formato de árvore para arquivos hierárquicos

## ⚙️ Power Features (Low Priority)

- Suporte a múltiplos arquivos e padrões (globs)
- Tratamento de arquivos binários (detecção e aviso)
- Limite de tamanho de arquivo (ex: 10MB)
- Melhoria nas mensagens de confirmação (detalhes adicionais)
- Listar itens removidos (`--removed`), desfazer remoção, hard delete (`cleanup`)
- Remover múltiplos itens, confirmação de remoção
- Melhorias na exibição de saída e mensagens de erro
- Suporte a Markdown

## Referências para Evolução

Os logs históricos em `docs/logs/` documentam todas as decisões e iterações. Para evoluir os comandos, consultar:

- `docs/logs/2025-12-12_123935__CODEX__session-status_MVP-CLOSURE.md` — Estado atual e backlog
- `docs/logs/2025-12-12_105000__QWEN__session-list_REFINEMENT.md` — Decisões arquiteturais sobre fontes de dados
- `docs/logs/2025-12-12_171122__QWEN__context-list_REFINEMENT.md` — Backlog técnico e oportunidades de melhoria
- `docs/logs/2025-12-12_162945__QWEN__context-remove_REFINEMENT.md` — Backlog técnico e oportunidades de melhoria
- `docs/logs/2025-12-12_171900__QWEN__run_REFINEMENT.md` — Backlog técnico e oportunidades de melhoria
## 🚨 UX Improvements (QWEN Feedback - 12/12)
- **Spinner de Execução:** Implementar feedback visual animado em `src/maestro/tools.py` para ferramentas reais (não-mock).
- **Feedback de Contexto:** O comando `context remove` deve exibir resumo do estado pós-remoção ("Item removido. X itens restantes.").

## 📊 Observabilidade e Custos (New)
- **Auditoria de Tokens:** Capturar métricas reais de consumo (tokens de entrada/saída) parseando o output JSON das ferramentas.
- **Estimativa de Custos:** Calcular e registrar o custo ($) de cada run no `meta.json`.
