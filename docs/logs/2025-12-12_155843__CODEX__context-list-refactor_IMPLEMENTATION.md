# CODEX — Refatoração: `maestro context list`
Timestamp: 2025-12-12 15:58:43

## O que foi refatorado
- `context_list` agora reutiliza `require_active_session` para validar sessão ativa e metadados antes da listagem.
- `require_active_session` passou a cobrir os mesmos cenários do comando (diretório `.maestro`, leitura de `session.json`, sessão finalizada) garantindo mensagens compatíveis.

## Linhas de código removidas (duplicação)
- Removida a sequência de validações manuais em `context_list` (existência de `.maestro/`, sessão ativa, leitura e estado de `session.json`).

## Linhas de código modificadas
- `require_active_session` agora verifica `.maestro`, lê `session.json` com tratamento de erros específicos e mantém o bloqueio de sessão finalizada com mensagem compatível.
- `context_list` captura `RuntimeError` de `require_active_session`, imprime a mensagem em `stderr` e encerra com código 1 em caso de falha.

## Testes realizados (antes/depois)
- Contexto com múltiplos itens  
  - Comandos: `./bin/maestro session start teste-refactor`; `./bin/maestro context add README.md`; `./bin/maestro context add 1-PROJECT.md`; `./bin/maestro context list`  
  - Saída antes: duas entradas `ctx-0001` e `ctx-0002` listadas com os mesmos hashes e tamanhos esperados.  
  - Saída depois: idêntica (duas entradas `ctx-0001` e `ctx-0002`, mesmos hashes/tamanhos).
- Contexto vazio  
  - Comandos: `./bin/maestro session start teste-vazio`; `./bin/maestro context list`  
  - Saída antes: `Contexto vazio. Use 'maestro context add <arquivo>' para adicionar itens`  
  - Saída depois: idêntica.
- Sem sessão ativa  
  - Comandos: `mv .maestro/sessions/active .maestro/sessions/active.bak`; `./bin/maestro context list`; restauração do arquivo `active`  
  - Saída antes: `Nenhuma sessão ativa. Use 'maestro session start <nome>'.` (retorno 1)  
  - Saída depois: idêntica (retorno 1).

## Confirmação de comportamento idêntico
- Saídas de `context list` antes e depois coincidem para todos os cenários testados (conteúdo, mensagens e códigos de retorno inalterados).

## Próximos passos
- Revisão pela GEMINI para confirmar remoção da duplicação e manutenção do comportamento.
