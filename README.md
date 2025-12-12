# Maestro

Orquestrador de CLIs de IA focado em gerenciar sessões, contexto e execução sequencial de ferramentas em um único terminal.

Estado atual:
- CLI disponível em `bin/maestro`.
- Comandos implementados:
  - `maestro session start <nome>` (cria estrutura em `.maestro/` e marca a sessão como ativa).
  - `maestro session list` (somente leitura) lê `.maestro/sessions/index.json` e, quando existir, cada `<sessao>/session.json` para usar `state` e `updated_at` como fonte canônica. A sessão ativa é resolvida por ordem de precedência: arquivo `.maestro/sessions/active` (se existir) e, só na ausência dele, o campo `active` do índice.
  - `maestro session status` (somente leitura) mostra os metadados da sessão ativa, respeitando as mesmas regras de resolução do `session list`.
  - `maestro context add <arquivo>` (adiciona arquivos ao contexto da sessão ativa).
  - `maestro context list` (lista os itens do contexto da sessão ativa).
  - `maestro context remove <id>` (remove itens do contexto da sessão ativa).
  - `maestro use <ferramenta>` (define a ferramenta ativa para a sessão).
  - `maestro run "<prompt>"` (executa a ferramenta ativa com o contexto da sessão).
- O nome da sessão deve conter pelo menos um caractere alfanumérico (nomes vazios ou só com símbolos retornam erro).
- Status: ✅ MVP Feature Complete. Todos os comandos previstos no `README.md` core estão funcionais (exceto `show` e `use-output` que são auxiliares).

Formato do `session list`:
- Primeira linha indica a sessão ativa ou informa divergência (ex.: arquivo `active` apontando para id ausente).
- Cada sessão vem como `*` (ativa) ou `-` (inativa) seguido do id; se o diretório ou `session.json` estiver faltando, aparece `[órfã]`.
- Campos exibidos: `slug`, `estado`, timestamps de criação/atualização e, se houver, finalização.

Para testar o binário localmente:
```bash
chmod +x bin/maestro
./bin/maestro session start teste
```
