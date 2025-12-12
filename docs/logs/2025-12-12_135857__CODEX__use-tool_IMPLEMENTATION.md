# CODEX — Implementação: maestro use

Timestamp: 2025-12-12 13:58

Relacionado a: `maestro use <nome-da-ferramenta>`

## Objetivo desta etapa
Permitir selecionar a ferramenta de IA que será usada no próximo `maestro run`, gravando a escolha em `session.json`.

## O que foi implementado
- Novo subcomando `maestro use <nome>` com validação de sessão ativa (respeita bloqueio de sessões finalizadas).
- Aceita qualquer string não vazia para a ferramenta (MVP não valida catálogo).
- Atualiza `tool_active` e `updated_at` em `.maestro/sessions/<id>/session.json` e confirma no terminal.
- `print_usage` ampliado para exibir a sintaxe do comando.

## Arquivos modificados
- `bin/maestro`

## Escrita em disco
- Apenas `session.json` da sessão ativa é atualizado ao executar `maestro use`.

## Testes
Automatizados: não há.

Sugestões de testes manuais:
1) Sessão ativa válida: `./bin/maestro session start teste && ./bin/maestro use codex` → verifica `tool_active: "codex"` em `session.json` e mensagem no terminal.
2) Sem sessão ativa: `rm -f .maestro/sessions/active && ./bin/maestro use codex` → erro sobre ausência de sessão ativa.
3) Nome vazio: `./bin/maestro use "   "` → erro de argumento obrigatório.
4) Sessão finalizada (editar state para `finalizada`): comando deve ser bloqueado com mensagem de erro.
