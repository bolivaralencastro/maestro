# CODEX — Encerramento MVP-0: `maestro session status`

Timestamp: 2025-12-12 12:39:35

## Decisões para o MVP
- Implementado agora: comando `maestro session status` read-only, resolve sessão ativa via `.maestro/sessions/active` com fallback para `active: true` no índice quando o arquivo não existe, valida presença no índice e no diretório, imprime metadados básicos de `session.json` (id, slug, state, tool_active, timestamps, counters, stats).
- Postergado conscientemente: alinhar a fonte única da sessão ativa eliminando o fallback ao índice; exibir contexto ativo (`context/active.json`) e última saída (`outputs/last_output.json`) conforme contrato do comando; endurecer diagnóstico de corrupção de JSON e mensagens de erro orientadas a ação; padronizar mensagens/formatos com `session list`; automatizar testes.

## Backlog técnico (não implementado neste ciclo)
- Tornar `.maestro/sessions/active` a única fonte de verdade (sem fallback automático para o índice) e sinalizar divergências como aviso.
- Incluir no status a lista de IDs do contexto ativo e a referência ao `last_output` (run_id + caminho).
- Melhorar tratamento de erros: avisar explicitamente quando arquivos JSON estiverem corrompidos ou metadados faltarem.
- Harmonizar mensagens e etiquetas de inconsistência entre `session status` e `session list`.
- Adicionar testes (mesmo manuais/guiados) cobrindo casos de ausência de `.maestro/`, sessão ativa inconsistente e exibição de contexto/última saída.

## Estado do comando
O comando `maestro session status` está **FECHADO no MVP-0** (sem novas alterações obrigatórias neste ciclo).

## Next: Mistral
- Registrar em `EVOLUTION.md` que `maestro session status` foi fechado no MVP-0 com leitura de metadados básicos e fallback controlado, mas mantendo pendências (fonte única do ativo, exibição de contexto/last_output, diagnóstico robusto).
- Incluir no backlog os itens listados na seção "Backlog técnico".
- Não reabrir este comando neste MVP; evoluções futuras devem ser tratadas em ciclos posteriores.
