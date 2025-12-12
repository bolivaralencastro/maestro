# STORAGE_LAYOUT

## Visão geral
- Persistência local em `.maestro/` no diretório raiz do repositório (motivo: portátil, versionável junto ao projeto e sem poluir `$HOME`; apenas configuração global opcional em `.maestro/config`).
- Cada sessão é um diretório nomeado com `slug--<id_curto>` onde `slug` vem do nome fornecido e `<id_curto>` é um sufixo aleatório base36 de 6 caracteres para evitar colisões (`session start` falha se já existir o mesmo nome completo).
- Metadados em JSON (simples de parse para CLIs, estável, fácil de serializar/deserializar sem dependências).
- Blobs de contexto (textos e snapshots de arquivos) gravados em arquivos `.txt` separados para preservar conteúdo bruto e evitar inflar JSON.
- Runs ficam em subpastas numeradas (`0001`, `0002`...) contendo prompt, contexto enviado, status, timestamps e outputs.
- Contexto ativo é uma lista referencial; o histórico completo de contextos (incluindo itens removidos/antigos) permanece nos metadados de itens.

## Estrutura de diretórios
```
.maestro/
├─ config/
│  └─ tools.json                 # catálogo local de ferramentas (para tool list/check)
├─ sessions/
│  ├─ index.json                 # resumo de sessões (id, slug, estado, timestamps)
│  ├─ active                     # contém o id da sessão ativa (para session switch/status)
│  └─ <slug>--<id_curto>/
│     ├─ session.json            # metadados principais da sessão
│     ├─ context/
│     │  ├─ active.json          # ids em uso no contexto ativo (ordenados)
│     │  ├─ items/               # metadados por item de contexto
│     │  │  └─ ctx-0001.json
│     │  └─ blobs/               # conteúdo estático (textos, snapshots de arquivos, saídas promovidas)
│     │     └─ ctx-0001.txt
│     ├─ runs/
│     │  └─ 0001/
│     │     ├─ meta.json         # prompt source, tool, status, timestamps, flags
│     │     ├─ prompt.txt        # texto original enviado
│     │     ├─ sent_context.json # contexto efetivamente enviado (refs + digests)
│     │     └─ output.txt        # stdout da ferramenta (se houver)
│     ├─ outputs/
│     │  ├─ last_output.json     # referência ao último run com saída
│     │  └─ relevant.json        # lista de outputs marcados como relevantes + motivos
│     └─ exports/                # arquivos gerados por maestro export (quando usado)
└─ logs/ (opcional)              # diagnósticos de tool check/list; pode ser limpo
```

## Esquemas de metadados

### `.maestro/config/tools.json`
- `tools`: array de objetos `{ name, path?, last_check?, status?, notes? }`
  - `tool list` lê daqui; `tool check` atualiza `last_check`, `status` (ok/warn/missing), `notes` (ex.: config ausente).

### `.maestro/sessions/index.json`
- `sessions`: array `{ id, slug, state, created_at, updated_at, finalized_at?, active? }`
- Usado por `session list`; atualizado em `session start/end/delete/switch`.

### `.maestro/sessions/active`
- Contém somente o `id` da sessão ativa (string). Lido por comandos que dependem do alvo atual (`run`, `context add`, `use`, `status`, `session switch` atualiza este arquivo).

### `session.json`
- `id`: `<slug>--<id_curto>`
- `slug`: slug original (kebab-case).
- `state`: `iniciada|com_contexto|executando|com_saida|finalizada|abortada`.
- `tool_active`: nome da ferramenta selecionada via `use` (ou `null`).
- `created_at`, `updated_at`, `finalized_at?`, `aborted_at?`, `abort_reason?`
- `counters`: `{ run_seq: <int>, ctx_seq: <int> }` para gerar nomes `0001`, `ctx-0001`.
- `stats`: `{ runs_total, runs_success, runs_error }`
- `notes?`: livre (ex.: objetivo da sessão).

### `context/active.json`
- `items`: array ordenado de ids (`ctx-0001`, `ctx-0002`, ...) representando o contexto ativo.
- `last_output_ref?`: id do run considerado `last_output` para facilitar `context use-output last`.

### `context/items/ctx-XXXX.json`
- `id`: `ctx-0001`
- `kind`: `file|text|output`
- `source`: se `file`, `{ path_rel, added_at, digest, mtime?, size }`; se `text`, `{ added_at }`; se `output`, `{ run_id, added_at }`
- `labels`: array opcional (`["initial"]`, `["last_output"]`, etc.)
- `snapshot`: `{ blob: "../blobs/ctx-0001.txt", digest }` garantindo a versão estável usada quando foi adicionada.
- `state`: `active|removed`
- `removed_at?`
- `notes?`
- Política: mesmo se o arquivo do projeto for alterado/deletado depois, o snapshot continua acessível.

### `runs/000N/meta.json`
- `id`: `0001`
- `tool`: nome da ferramenta usada.
- `prompt_source`: `cli|stdin|file` + `prompt_file?`
- `flags`: `{ dry_run: bool, confirm: bool, confirmed_at? }`
- `status`: `pending|running|success|error|canceled|dry`
- `created_at`, `started_at?`, `finished_at?`
- `context_refs`: ids enviados (ex.: `["ctx-0001","ctx-0003"]`)
- `context_version`: array com `{ id, digest }` espelhando `sent_context.json` (para detectar divergência posterior).
- `output_ref?`: `{ path: "output.txt", size?, digest? }`
- `error?`: mensagem de erro, se houver.

### `runs/000N/sent_context.json`
- Array de objetos `{ id, kind, snapshot_blob, digest, path_rel?, role? }`
- Captura exatamente o material enviado para a ferramenta (inclui textos e snapshots, não apenas referências).

### `outputs/last_output.json`
- `{ run_id, path: "../runs/000N/output.txt", timestamp }`
- Atualizado após cada run bem-sucedido com saída.

### `outputs/relevant.json`
- `{ items: [ { run_id, note?, added_at } ] }`
- `context use-output <id>` adiciona o run à lista e cria item de contexto do tipo `output` apontando para o blob correspondente em `context/blobs/`.

### `exports/<timestamp>-<format>.<ext>`
- Gerado por `maestro export`; contém sessão inteira no formato escolhido (`md` ou `json`), incluindo anexos a partir de `runs/*/output.txt` e `context/blobs/*`.

## Fluxos (mapeados aos comandos)
- **start (`session start <nome>`):** gerar `slug`, `id`, criar pasta e `session.json` (state `iniciada`), atualizar `sessions/index.json` e `.maestro/sessions/active`.
- **session switch `<nome>`:** valida existência, grava id em `.maestro/sessions/active`, atualiza campo `active?` no `index`.
- **add (`context add <arquivo|texto>`):** incrementa `ctx_seq`; cria `context/items/ctx-XXXX.json`; salva snapshot em `context/blobs/ctx-XXXX.txt` (para arquivo: copia conteúdo atual e digest; guarda `path_rel` para referência futura); marca item como `active` e inclui em `context/active.json`; estado da sessão vai para `com_contexto`.
- **use-output `<id|last>`:** resolve run/output, copia conteúdo para novo blob de contexto, cria item `kind: output` e marca `labels` apropriadas; atualiza `relevant.json`.
- **use (`maestro use <tool>`):** grava `tool_active` em `session.json`; opcionalmente marca timestamp de seleção.
- **run (`maestro run ...`):**
  - Aloca nova pasta `runs/000N` usando `run_seq`.
  - Salva prompt em `prompt.txt`; registra `prompt_source` (`cli`, `stdin`, `file` com caminho).
  - Em `sent_context.json`, materializa as versões (blobs) dos ids listados em `context/active.json`, com digest das snapshots; meta inicial `status=pending`.
  - Se `--dry`, não executa tool: `status=dry`, sem `output.txt`; meta registra preview do destino.
  - Se `--confirm`, grava `flags.confirm=true` e `confirmed_at` quando o usuário aceita.
  - Durante execução: `status=running`; ao terminar, `status=success|error|canceled`; salva `output.txt` (stdout completo) e `output_ref` no meta.
  - Atualiza `outputs/last_output.json` em caso de sucesso; estado da sessão vai para `com_saida`.
- **show (`maestro show [id|last]`):** lê `outputs/last_output.json` ou `runs/<id>/output.txt`.
- **session status/list:** consultam `session.json`, `active.json`, `outputs/last_output.json`, `sessions/index.json`.
- **session end:** define `state=finalizada`, `finalized_at`; congela `context/active.json` (não mais alterada) e impede novos runs; `index.json` atualizado.
- **session delete `<nome>`:** remove diretório da sessão e entrada no `index` (pode mover para lixeira se desejado).
- **tool list/check:** usam `config/tools.json`; `tool check` opcionalmente escreve logs em `.maestro/logs/tool-check-*.log`.
- **run --stdin / --file:** apenas altera `prompt_source` e opcionalmente armazena `prompt_file` (relativo ao repo) para rastreabilidade.
- **maestro export [--format md|json] [--output <path>]:** lê sessão, runs, blobs e outputs; escreve arquivo em `exports/` (ou caminho fornecido) com histórico completo + anexos referenciados; utiliza `context/blobs` e `runs/*/output.txt` para embutir ou anexar.

## Como contexto é referenciado e versionado
- Referência primária: `id` (`ctx-XXXX`) listado em `context/active.json`.
- Para arquivos: `path_rel` sempre armazenado; snapshot fixo em `context/blobs/` com `digest` SHA-256 (ou equivalente). Se o arquivo do projeto mudar, `context/list` pode mostrar divergência via comparação de digest atual vs. `source.digest`.
- Para texto/output: conteúdo só existe na snapshot; não depende de arquivo externo.
- Cada run captura `sent_context.json` com os digests no momento do envio, garantindo auditabilidade mesmo se o item for atualizado/removido depois.
- Itens removidos permanecem com `state=removed` e snapshot preservada; não aparecem em `context/active.json`, mas seguem referenciáveis para histórico e export.

## Persistência de runs e outputs
- Cada run possui diretório próprio (`runs/000N`) com: `meta.json` (estado + tool + timestamps + flags), `prompt.txt`, `sent_context.json`, `output.txt` (quando houver).
- `last_output` é um apontador (`outputs/last_output.json`) para o run mais recente bem-sucedido.
- Outputs marcados como relevantes ficam listados em `outputs/relevant.json` e também podem virar itens de contexto (`kind: output`) com blob dedicado.

## Descarte e retenção mínima
- Pode ser descartado: logs de `tool check/list` em `.maestro/logs/`; runs com `status=dry` (sem execução real) podem ser limpos sem afetar histórico crítico.
- Retenção mínima: manter `session.json`, `context/items/*`, `context/blobs/*`, `runs/*/meta.json`, `runs/*/sent_context.json` e `outputs/last_output.json` por pelo menos 30 dias após `finalizada` ou até `session delete` explícito. `output.txt` de runs não marcados como relevantes pode ser limpo após 30 dias, desde que `relevant.json` e `last_output` não apontem para eles (preservar texto do run marcado como relevante copiando-o antes para `context/blobs/`).
- Ao limpar, atualizar `relevant.json` para remover referências quebradas e registrar em `session.json` (ex.: `cleanup_at`).

## Notas de segurança e privacidade
- Não gravar chaves/API secrets em lugar algum; `tools.json` deve conter apenas caminhos e status.
- Saídas de modelos podem conter dados sensíveis copiados do código; alertar o usuário ao exportar. `maestro export` deve incluir aviso quando incluir blobs de arquivos do projeto.
- Snapshots preservam conteúdo original; se for confidencial, use `session delete` ou limpeza seletiva dos blobs/outputs.
- Evitar gravar stderr ou logs verbosos no diretório da sessão salvo se requerido para debug (preferir `.maestro/logs/` e permitir limpeza).

## Exemplo de sessão (2 runs)
```
.maestro/
└─ sessions/
   ├─ index.json
   ├─ active
   └─ refatorar-pagamento--k9fz2p/
      ├─ session.json
      ├─ context/
      │  ├─ active.json
      │  ├─ items/
      │  │  ├─ ctx-0001.json          # arquivo src/pagamento.js (snapshot + digest)
      │  │  ├─ ctx-0002.json          # arquivo src/utils.js (snapshot + digest)
      │  │  └─ ctx-0003.json          # output do run 0001 marcado como relevante
      │  └─ blobs/
      │     ├─ ctx-0001.txt           # conteúdo de src/pagamento.js na data da adição
      │     ├─ ctx-0002.txt           # conteúdo de src/utils.js
      │     └─ ctx-0003.txt           # saída relevante do run 0001
      ├─ runs/
      │  ├─ 0001/
      │  │  ├─ meta.json              # tool=gemini, status=success, prompt_source=cli
      │  │  ├─ prompt.txt             # "Liste code smells..."
      │  │  ├─ sent_context.json      # refs a ctx-0001/0002 + digests
      │  │  └─ output.txt             # análise produzida
      │  └─ 0002/
      │     ├─ meta.json              # tool=codex, status=success, prompt_source=cli
      │     ├─ prompt.txt             # "Refatore o código original..."
      │     ├─ sent_context.json      # refs a ctx-0001/0002/0003 (com snapshot de output)
      │     └─ output.txt             # código refatorado
      ├─ outputs/
      │  ├─ last_output.json          # aponta para runs/0002/output.txt
      │  └─ relevant.json             # inclui run 0001 (análise) e opcionalmente 0002
      └─ exports/
         └─ 2024-05-07T12-00-00Z-md.md
```

