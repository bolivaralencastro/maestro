# Projeto "Maestro": Orquestrador de CLIs de IA

## 1. O Problema que Este Projeto Resolve

Desenvolvedores e power users que utilizam múltiplas CLIs de IA (ex: Gemini, Codex, Mistral, Qwen) enfrentam um fluxo de trabalho fragmentado e ineficiente. Cada ferramenta opera em seu próprio terminal, isolada das outras.

A transferência de contexto (código-fonte, logs, resultados de um comando) entre essas CLIs é um processo manual, repetitivo e propenso a erros. Não há um "espaço de trabalho" unificado, o que dificulta a orquestração de tarefas complexas que poderiam se beneficiar da especialização de diferentes modelos de IA em sequência.

Este projeto visa substituir a necessidade de gerenciar múltiplos terminais por uma interface única e coesa que orquestra os processos, gerencia o contexto e atribui responsabilidades de forma explícita.

## 2. Objetivos Iniciais (MVP)

O foco do MVP é validar a orquestração manual e o gerenciamento de contexto.

- **Interface Única:** Criar uma CLI ou TUI (Text-based User Interface) para macOS que sirva como ponto de entrada para todas as interações.
- **Gerenciamento de Contexto:** Permitir que o usuário defina um "contexto de trabalho" (um ou mais arquivos, ou blocos de texto) para uma tarefa específica.
- **Seleção de Ferramenta:** Permitir que o usuário escolha qual IA (ex: `gemini`, `codex`) será usada em cada etapa.
- **Passagem de Contexto:** Facilitar o envio do contexto atual como entrada para a CLI de IA selecionada.
- **Captura de Saída:** Capturar a saída (stdout) da ferramenta de IA e apresentá-la ao usuário, permitindo que ela seja usada como contexto para a próxima etapa.
- **Histórico Simples:** Manter um registro básico das operações realizadas (qual IA foi usada, qual foi o prompt) dentro de uma sessão.

## 3. O Que NÃO é Objetivo Agora (Fora do Escopo)

Para manter o foco e a viabilidade, os seguintes itens estão explicitamente fora do escopo inicial:

- **Automação Completa:** O objetivo não é criar pipelines autônomos. A interação é manual e guiada pelo usuário a cada passo.
- **Criação de CLIs ou Modelos:** O projeto não vai desenvolver novas IAs, apenas orquestrar as já existentes.
- **Interface Gráfica (GUI):** A solução será estritamente para o terminal (CLI/TUI).
- **Gerenciamento de Autenticação:** A ferramenta assumirá que as CLIs de IA subjacentes já estão instaladas e configuradas (API keys, etc.).
- **Execução Paralela:** As tarefas serão executadas sequencialmente.
- **Lógica Condicional:** Não haverá suporte para fluxos de trabalho com condicionais (ex: "se a saída de Gemini contiver X, então execute Codex").

## 4. Interação do Usuário

A interação será baseada em comandos. O usuário iniciará a ferramenta e operará dentro de sua sessão.

1.  **Inicia uma sessão:** `maestro start my-refactor-task`
2.  **Adiciona contexto:** `maestro add ./src/complex-module.py`
3.  **Seleciona uma ferramenta:** `maestro use gemini`
4.  **Executa um prompt:** `maestro run "Encontre bugs e code smells neste módulo"`
5.  **Revisa a saída:** A ferramenta exibe o resultado da análise.
6.  **Usa a saída como novo contexto (opcional) e muda de ferramenta:** `maestro use codex --context last_output`
7.  **Executa um novo prompt:** `maestro run "Refatore o código original com base na análise"`

## 5. Fluxo de Uso Básico (Exemplo)

Um fluxo de trabalho comum poderia ser a refatoração e documentação de um código existente:

1.  **Análise:** O usuário adiciona um arquivo de código ao contexto e usa o `gemini` para realizar uma análise de qualidade, identificando bugs e "code smells".
2.  **Revisão e Geração:** O usuário revisa o relatório. Em seguida, ele usa o `codex`, fornecendo o código original e o relatório da análise como contexto, com o prompt para "aplicar as correções sugeridas".
3.  **Ajuste Fino:** Após a refatoração, o usuário pode usar uma IA mais conversacional como o `mistral` para fazer ajustes finos, como "renomear a variável `x` para `user_count`".
4.  **Documentação:** Com o código finalizado no contexto, o usuário troca para o `gemini` novamente com o prompt "Gere a documentação em formato Markdown para esta função".
5.  **Finalização:** O usuário copia o código e a documentação gerados para seus arquivos finais.

## 6. Próximos Passos

- [ ] Detalhar a especificação da interface de comandos (CLI).
- [ ] Desenvolver um protótipo (Prova de Conceito) em uma linguagem de script (ex: Python, Go, ou mesmo um shell script robusto) para validar a interação com uma ou duas CLIs.
- [ ] Definir a estrutura de dados para o "contexto de trabalho" (como será armazenado e gerenciado).
- [ ] Pesquisar bibliotecas para a construção de uma TUI (ex: `Bubble Tea` em Go, `Textual` em Python) para uma experiência de usuário mais rica.