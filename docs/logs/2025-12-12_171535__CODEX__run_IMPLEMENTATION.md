# CODEX — Implementação: maestro run

Timestamp: 2025-12-12 17:15

Relacionado a: `maestro run`

## Objetivo desta etapa
Implementar o comando principal `maestro run "<prompt>"`, orquestrando validações da sessão, preparação de contexto, execução (mock/subprocesso) e persistência no layout de runs.

## O que foi implementado
- Validações iniciais: uso de `require_active_session`, bloqueio de sessões finalizadas, exigência de ferramenta ativa e prompt não vazio.
- Coleta do contexto ativo a partir de `context/active.json`, leitura de metadados/blobs (`context/items/*.json` + `context/blobs/*.txt`), construção de snapshot (`sent_context.json`) e do prompt final com separadores por item.
- Alocação sequencial de runs (`runs/000N`), gravação de `prompt.txt`, `meta.json` (status pendente/correndo/sucesso/erro, timestamps, contexto) e `sent_context.json`.
- Execução: modo simulado para ferramentas `mock/simulacao` (spinner simples + saída fictícia) e fallback via `subprocess.run` para demais ferramentas, tratando `FileNotFoundError` com sugestão de usar mock ou revisar PATH.
- Persistência de saída (`output.txt`), atualização de `outputs/last_output.json`, contadores/estatísticas em `session.json` (runs_total/success/error, run_seq) e estado para `com_saida` em casos de sucesso; erros mantêm estado anterior.
- Mensagens ao usuário: "Executando ..." + spinner opcional, exibição da saída capturada e confirmação final `Run <id> concluído. Saída salva.` ou erro descritivo.

## Arquivos modificados
- `bin/maestro`

## Testes
Manuais:
1) `python3 bin/maestro session start teste-run` → cria sessão.
2) `python3 bin/maestro context add README.md` → adiciona `ctx-0001`.
3) `python3 bin/maestro use mock` → define ferramenta simulada.
4) `python3 bin/maestro run "Resuma este arquivo"` → cria `runs/0001/` com meta, sent_context, prompt e output; `outputs/last_output.json` atualizado; estado da sessão em `com_saida`.
