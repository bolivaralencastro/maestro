# Modelo Conceitual de Sessão (Maestro)

## O que é uma sessão
- Um contêiner temporal e lógico que agrupa interações sequenciais do usuário com CLIs de IA sob um propósito único (ex.: refatorar módulo X).
- Mantém identidade (nome/slug), estado corrente e histórico mínimo para que o usuário e o sistema saibam onde estão e o que já foi feito.
- Existe somente enquanto o usuário estiver trabalhando naquele fluxo; encerrou ou foi finalizada, torna-se um registro consultável (se persistido).

## Estados de uma sessão
- `iniciada` — criada e identificada; sem contexto carregado.
- `com_contexto` — possui ao menos um item de contexto ativo (arquivos, blocos de texto, seleções de saída anteriores).
- `executando` — há uma chamada de ferramenta em andamento usando o contexto atual e uma entrada fornecida.
- `com_saida` — última execução produziu saída disponível para consulta/uso.
- `finalizada` — não aceita novas entradas, contexto congelado; pode ser consultada.
- `abortada` (opcional) — interrompida por erro ou cancelamento; pode manter artefatos parciais.

Observação: estados podem ter transições lineares simples (iniciada → com_contexto → executando → com_saida → finalizada) com loops entre `com_contexto` ↔ `executando` ↔ `com_saida` até o usuário finalizar.

## Evolução do contexto ao longo da sessão
- Contexto inicial: vazio ou com itens adicionados explicitamente pelo usuário.
- Adição: usuário inclui arquivos, trechos copiados, anotações ou seleciona saídas anteriores para compor o contexto ativo.
- Consumo: cada execução lê o contexto ativo; o sistema registra qual subconjunto foi enviado para a ferramenta (para rastreabilidade).
- Enriquecimento: saídas podem ser marcadas como novo contexto (inteiro ou parcial) e empilhadas; itens podem receber rótulos (ex.: `last_output`).
- Substituição/limpeza: usuário pode remover itens ou redefinir o contexto ativo; histórico de remoção pode ser opcionalmente registrado.
- Congelamento: ao finalizar, o contexto final é fixado para consulta; alterações posteriores não são permitidas nessa sessão.

## Entrada e saída
- Entrada:
  - Prompt/comando textual fornecido pelo usuário para a ferramenta de IA.
  - Seleção de ferramenta (ex.: `use gemini`) e parâmetros operacionais (ex.: temperatura, limites) — se estiverem no escopo do MVP.
  - Contexto ativo (referências a arquivos, blobs de texto, seleções de saída) enviado junto ao prompt.
- Saída:
  - stdout retornado pela ferramenta de IA.
  - Metadados da execução (qual ferramenta, timestamp, prompt usado, referência ao contexto enviado).
  - Status de execução (sucesso, erro, cancelamento).

## Persistência em disco (mínimo viável)
- Identidade da sessão: nome/slug, timestamps (criação, última atividade, finalização).
- Estado atual da sessão.
- Lista de itens de contexto ativos e seus metadados essenciais:
  - Referências de arquivos (path absoluto/relativo no momento da adição).
  - Blocos de texto livres armazenados como conteúdo estático.
  - Referências a saídas anteriores selecionadas como contexto (ex.: IDs).
- Histórico resumido de execuções:
  - Ferramenta usada, prompt, contexto referenciado, timestamp, status.
  - Pointers para saída armazenada (ver abaixo).
- Saídas persistidas necessárias:
  - Última saída completa de cada execução (texto bruto) e, opcionalmente, saídas marcadas pelo usuário como relevantes.
- Marcas de controle: flags de finalização/abortamento e motivo, se houver.

## Itens que podem ser descartados (ou armazenados apenas em memória)
- Saídas intermediárias não marcadas como relevantes pelo usuário (se houver política de retenção curta).
- Logs detalhados de execução (debug) além do resumo necessário para histórico.
- Versões antigas de contexto que foram substituídas e não marcadas para retenção.
- Artefatos temporários gerados durante execução (buffers, arquivos temporários).

## Fluxo lógico resumido
1. Criar sessão (`iniciada`), registrar identidade.
2. Adicionar contexto (torna-se `com_contexto`).
3. Selecionar ferramenta e executar com prompt e contexto (`executando` → `com_saida`).
4. Avaliar saída: opcionalmente promover saída ou trecho a contexto ativo.
5. Repetir passos 3–4 quantas vezes necessário (loop).
6. Finalizar: congelar estado, persistir histórico e contexto final (`finalizada` ou `abortada`).
