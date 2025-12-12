# CODEX — Implementação: `maestro context list`

Timestamp: 2025-12-12 15:26:47

## O que foi implementado
- Novo subcomando `maestro context list` em `bin/maestro`, com validações de existência de `.maestro/`, sessão ativa e bloqueio de sessão finalizada.
- Leitura do contexto ativo a partir de `.maestro/sessions/<id>/context/active.json` e resolução de metadados por item em `context/items/<id>.json`.
- Formatação de saída em linha única por item com tipo, origem, tamanho humanizado e hash abreviado.
- Atualização do `print_usage` para incluir o novo comando.

## Decisões técnicas
- Comando estritamente read-only: nenhuma chamada a `ensure_base_structure` ou escrita em disco; somente leitura dos arquivos exigidos.
- Tratamento explícito para JSON corrompido em `session.json` e `active.json`, reportando erro e abortando a listagem.
- Origem exibida de forma amigável: caminhos relativos recebem prefixo `./`; itens de texto mostram `[texto]`; outputs mostram `saída do run <id>` quando disponível.
- Hash abreviado usando os primeiros 7 caracteres com reticências quando necessário; tamanho formatado em unidades IEC simples.
- Quando `size` não está nos metadados, tenta usar o snapshot em `context/blobs/<id>.txt` para preencher o tamanho sem escrever nada.

## Casos de borda tratados
- `.maestro/` ausente → erro: "Nenhuma sessão foi criada ainda."
- Sessão ativa ausente → erro: "Nenhuma sessão ativa. Use 'maestro session start <nome>'."
- Sessão finalizada → erro: "Sessão finalizada não pode ser modificada"
- Contexto vazio (arquivo inexistente, sem items ou lista vazia) → mensagem guiando para `context add`.
- Item referenciado sem metadados → linha com `[metadados ausentes]`.
- Item com JSON inválido ou erro de leitura → linha com `[erro ao ler metadados]`.

## Testes manuais
1) Contexto com múltiplos itens  
   - `./bin/maestro session start teste-contexto-lista`  
   - `./bin/maestro context add README.md`  
   - `./bin/maestro context add 1-PROJECT.md`  
   - `./bin/maestro context list` → listou 2 itens com tipo `arquivo`, origem relativa, tamanho e hash abreviado.

2) Contexto vazio  
   - `./bin/maestro session start teste-contexto-vazio`  
   - `./bin/maestro context list` → exibiu "Contexto vazio. Use 'maestro context add <arquivo>' para adicionar itens".

3) Sem sessão ativa  
   - `mv .maestro/sessions/active .maestro/sessions/active.bak`  
   - `./bin/maestro context list` → erro "Nenhuma sessão ativa. Use 'maestro session start <nome>'." (retorno 1)  
   - `mv .maestro/sessions/active.bak .maestro/sessions/active` para restaurar.

## Próximos passos
- Revisão pela Gemini focando em mensagens de erro, cobertura de casos de borda e aderência ao formato de saída.
