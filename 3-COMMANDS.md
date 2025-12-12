# Comandos da CLI Maestro

Este documento define a interface de linha de comando (CLI) para o orquestrador Maestro. Os comandos são projetados para gerenciar sessões de trabalho, manipular o contexto e executar ferramentas de IA de forma sequencial e controlada.

## Resumo dos Comandos

| Comando Principal | Subcomandos | Descrição | Tipo de Operação |
| :---------------- | :------------------ | :------------------------------------------------------------------ | :------------------- |
| `maestro session` | `start`, `list`, `status`, `end`, `delete` | Gerencia o ciclo de vida das sessões de trabalho. | Leitura e Escrita |
| `maestro context` | `add`, `list`, `remove`, `use-output` | Gerencia os arquivos, textos e saídas que compõem o contexto. | Leitura e Escrita |
| `maestro use` | | Define qual ferramenta de IA será usada na próxima execução. | Escrita |
| `maestro run` | | Executa a ferramenta de IA selecionada com o contexto atual. | Escrita |
| `maestro show` | | Exibe a última saída gerada ou um artefato específico da sessão. | Leitura |

---

## Detalhe dos Comandos

### 1. `maestro session`

Gerencia as sessões de trabalho. Uma sessão encapsula um fluxo de trabalho completo.

- **`session start <nome-da-sessao>`**
  - **Sintaxe:** `maestro session start <nome-da-sessao>`
  - **Descrição:** Cria e ativa uma nova sessão de trabalho.
  - **Tipo:** Altera o estado (write).

- **`session list`**
  - **Sintaxe:** `maestro session list`
  - **Descrição:** Lista todas as sessões existentes e seus estados.
  - **Tipo:** Apenas leitura (read-only).

- **`session status`**
  - **Sintaxe:** `maestro session status`
  - **Descrição:** Mostra o estado detalhado da sessão ativa (contexto, ferramenta, última saída).
  - **Tipo:** Apenas leitura (read-only).

- **`session end`**
  - **Sintaxe:** `maestro session end`
  - **Descrição:** Finaliza a sessão ativa, congelando seu estado.
  - **Tipo:** Altera o estado (write).

- **`session delete <nome-da-sessao>`**
  - **Sintaxe:** `maestro session delete <nome-da-sessao>`
  - **Descrição:** Apaga permanentemente uma sessão e seus artefatos.
  - **Tipo:** Altera o estado (write).

### 2. `maestro context`

Controla o contexto de trabalho da sessão ativa.

- **`context add <caminho-do-arquivo | "texto">`**
  - **Sintaxe:** `maestro context add ./meu/arquivo.js` ou `maestro context add "Um bloco de texto livre"`
  - **Descrição:** Adiciona um arquivo ou um bloco de texto ao contexto da sessão ativa.
  - **Tipo:** Altera o estado (write).

- **`context list`**
  - **Sintaxe:** `maestro context list`
  - **Descrição:** Lista os itens (com seus IDs) que compõem o contexto atual.
  - **Tipo:** Apenas leitura (read-only).

- **`context remove <id-do-item>`**
  - **Sintaxe:** `maestro context remove <id-do-item>`
  - **Descrição:** Remove um item específico do contexto usando o ID fornecido por `context list`.
  - **Tipo:** Altera o estado (write).

- **`context use-output <id-da-saida|last>`**
  - **Sintaxe:** `maestro context use-output last`
  - **Descrição:** Adiciona uma saída de execução anterior (por padrão, a última) ao contexto atual.
  - **Tipo:** Altera o estado (write).

### 3. `maestro use`

Define a ferramenta de IA para a próxima execução.

- **Sintaxe:** `maestro use <nome-da-ferramenta>`
- **Descrição:** Seleciona a CLI de IA (ex: `gemini`, `codex`) a ser usada no próximo comando `run`.
- **Tipo:** Altera o estado (write).

### 4. `maestro run`

Executa a tarefa principal, enviando o prompt e o contexto para a ferramenta selecionada.

- **Sintaxe:** `maestro run "<prompt para a IA>"`
- **Descrição:** Executa a ferramenta ativa, passando o contexto atual e o prompt fornecido.
- **Tipo:** Altera o estado (write).

### 5. `maestro show`

Exibe o conteúdo da última saída gerada.

- **Sintaxe:** `maestro show [id-da-saida|last]`
- **Descrição:** Imprime no terminal o conteúdo da última saída (`last`) ou de uma saída específica.
- **Tipo:** Apenas leitura (read-only).

---

## Exemplos de Fluxo de Uso

1.  **Iniciar e preparar a sessão:**
    ```bash
    # Cria e ativa uma nova sessão para refatorar um módulo
    maestro session start refatorar-modulo-pagamento

    # Adiciona o arquivo principal e um helper ao contexto
    maestro context add ./src/pagamento.js
    maestro context add ./src/utils.js

    # Lista o contexto para confirmar
    maestro context list
    ```

2.  **Analisar o código:**
    ```bash
    # Seleciona o Gemini para análise de código
    maestro use gemini

    # Pede para a IA encontrar problemas no contexto atual
    maestro run "Encontre e liste os code smells e possíveis bugs nos arquivos em contexto"

    # Visualiza a análise gerada
    maestro show
    ```

3.  **Refatorar com base na análise:**
    ```bash
    # Adiciona a análise ao contexto para a próxima etapa
    maestro context use-output last

    # Troca para uma ferramenta de geração de código
    maestro use codex

    # Pede a refatoração com base no código original e na análise
    maestro run "Refatore o código original aplicando as melhorias sugeridas na análise"

    # Visualiza o novo código refatorado
    maestro show
    ```

4.  **Finalizar a sessão:**
    ```bash
    # Marca a sessão como concluída
    maestro session end
    ```

## Observações de Comportamento

- **Sessão Ativa:** A maioria dos comandos opera no escopo de uma sessão ativa. `session start` define qual sessão está ativa. No futuro, um comando `session switch <nome>` poderia ser adicionado para alternar entre sessões.
- **Imutabilidade:** Comandos de `leitura` são seguros e não alteram nenhum dado. Comandos de `escrita` modificam o estado da sessão (adicionando contexto, registrando saídas, etc.) e devem ser usados com mais atenção.
- **IDs:** Itens de contexto e saídas de execução recebem IDs sequenciais ou hashes curtos para serem referenciados em outros comandos (ex: `context remove`, `show`).
- **Saídas:** Por padrão, as saídas são formatadas para leitura humana. Flags como `--output json` poderiam ser implementadas no futuro para facilitar a integração com outros scripts.
