# CODEX — Implementação: maestro context add

Timestamp: 2025-12-12 13:34

Relacionado a: `maestro context add`

## Objetivo desta etapa
Implementar o subcomando de escrita para adicionar arquivos locais ao contexto da sessão ativa, criando snapshot imutável e metadados conforme o layout.

## O que foi implementado
- Validação de sessão ativa a partir de `.maestro/sessions/active`, bloqueando sessões finalizadas ou inexistentes.
- Fluxo de ingestão de arquivo: valida existência/leitura, calcula SHA-256, captura mtime e tamanho, resolve caminho relativo ao repositório.
- Geração sequencial de IDs `ctx-XXXX` usando `counters.ctx_seq` de `session.json` e incremento persistido.
- Criação de snapshot em `context/blobs/<ctx-id>.txt` e metadados em `context/items/<ctx-id>.json` com `kind: file`, `source` e `snapshot` (digest duplicado para rastreabilidade).
- Atualização de `context/active.json` preservando campos existentes e inclusão do novo ID; atualização de `session.json` (estado para `com_contexto` quando aplicável, `updated_at`).
- Mensagem de sucesso no terminal com o ID e a sessão alvo; `print_usage` atualizado com o novo comando.

## Arquivos modificados
- `bin/maestro`

## Escrita em disco
- Snapshots e metadados são gravados dentro de `.maestro/sessions/<id>/context/` ao executar `maestro context add`.

## Testes
Automatizados: não há.

Sugestões de testes manuais:
1) Sem sessão ativa: `rm -f .maestro/sessions/active && ./bin/maestro context add README.md` → erro sobre sessão ativa.
2) Sessão ativa válida + arquivo existente: `./bin/maestro session start teste && ./bin/maestro context add README.md` → cria `ctx-0001` com blob, item e active atualizados.
3) Sessão finalizada: editar `session.json` para `state: "finalizada"` e tentar adicionar → erro bloqueando alteração.
4) Caminho inválido: `./bin/maestro context add arquivo_inexistente` → erro de arquivo não encontrado.
