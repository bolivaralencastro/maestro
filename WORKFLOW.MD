# Protocolo de Desenvolvimento Multi-Agente (Maestro Workflow)

Este documento define o processo de engenharia de software utilizado no projeto Maestro, baseado na orquestração de 4 Agentes de IA especializados operando via CLI em terminais isolados.

## 1. A Equipe Virtual (Roles)

O desenvolvimento é dividido em 4 papéis rígidos. Cada agente possui um arquivo de definição de personalidade (ex: `CODEX.md`) que deve ser respeitado estritamente.

| Agente | CLI / Prompt | Função Principal | Responsabilidade | Saída Esperada |
| :--- | :--- | :--- | :--- | :--- |
| **CODEX** | `codex` | **Executor Técnico** | Escrever código, criar arquivos, implementar features baseadas em specs. | Código-fonte + Log de Implementação. |
| **GEMINI** | `gemini` | **Revisor Técnico** | Auditar segurança, integridade de dados e aderência à spec. Não escreve código. | Log de Revisão (APROVADO/REJEITADO). |
| **QWEN** | `qwen` | **Refinador de Produto** | Avaliar UX, casos de borda e sugerir melhorias para o backlog. Não altera código. | Log de Refinamento + Itens de Backlog. |
| **MISTRAL** | `mistral` | **Historiador** | Consolidar a evolução do projeto e atualizar a documentação mestre. | Atualização do `EVOLUTION.md`. |

**O Quinto Elemento: O Orquestrador (Você/IA Central)**
- Define qual tarefa será executada.
- Gera os prompts para os agentes acima.
- Copia e cola as saídas de um terminal para o input do próximo.
- Toma decisões estratégicas baseadas nos pareceres dos agentes.

## 2. O Ciclo de Desenvolvimento (The Loop)

Para cada nova funcionalidade ou tarefa, o ciclo deve seguir **obrigatoriamente** esta ordem linear:

### Passo 1: Definição (Orquestrador)
O Orquestrador decide qual o próximo passo lógico (baseado no `EVOLUTION.md` e `PROJECT.md`).

### Passo 2: Implementação (CODEX)
- **Input:** Especificação técnica (o que fazer) + referências aos arquivos de arquitetura.
- **Ação:** Escreve o código em `bin/` ou `src/`.
- **Output:** Cria arquivo `docs/logs/YYYY...__CODEX__<task>_IMPLEMENTATION.md`.

### Passo 3: Auditoria (GEMINI)
- **Input:** O log gerado pelo CODEX + Código fonte atual.
- **Ação:** Verifica se o código quebra regras de segurança ou arquitetura (ex: `STORAGE_LAYOUT.md`).
- **Decisão:**
  - *Se Aprovado:* O ciclo continua.
  - *Se Rejeitado:* O ciclo volta para o **Passo 2** (CODEX) com as correções exigidas.
- **Output:** Cria arquivo `docs/logs/YYYY...__GEMINI__<task>_REVIEW.md`.

### Passo 4: Refinamento (QWEN)
- **Input:** Logs do CODEX e GEMINI.
- **Ação:** Analisa usabilidade (UX) e o que ficou faltando (débito técnico consciente).
- **Output:** Cria arquivo `docs/logs/YYYY...__QWEN__<task>_REFINEMENT.md` com veredito "MVP Adequado" ou "Refinamento Necessário".

### Passo 5: Consolidação (MISTRAL)
- **Input:** Todos os logs do ciclo atual.
- **Ação:** Atualiza o arquivo `EVOLUTION.md`.
- **Output:** `EVOLUTION.md` atualizado com a nova linha do tempo e status do projeto.

## 3. Estrutura de Comunicação (Prompts)

Os agentes não conversam entre si diretamente. A comunicação é assíncrona baseada em arquivos de Log.
Ao acionar um agente, o Orquestrador deve sempre usar a seguinte estrutura de Prompt:

**Para o CODEX:**
```text
Tarefa: [Nome da Tarefa]
Contexto: [Por que estamos fazendo isso?]
Referências: [Quais arquivos ler? ex: 3-COMMANDS.md]
Requisitos:
1. [Requisito técnico 1]
2. [Requisito técnico 2]
Output Esperado: Código + Log de Implementação.
```

**Para o GEMINI:**
```text
Tarefa: Revisão Técnica de [Nome da Tarefa]
Entrada: [Caminho do Log do CODEX]
Checklist:
1. [Risco de Segurança?]
2. [Aderência à Spec?]
Output Esperado: Log de Revisão com Parecer (APROVADO/REJEITADO).
```

**Para o QWEN:**
```text
Tarefa: Refinamento de UX de [Nome da Tarefa]
Entrada: [Log CODEX] + [Log GEMINI]
Objetivo: Identificar melhorias e itens para Backlog.
Output Esperado: Log de Refinamento + Lista de Sugestões.
```

**Para o MISTRAL:**
```text
Tarefa: Atualização do Histórico (Ciclo [Nome da Tarefa])
Entrada: [Lista de todos os logs do ciclo]
Ação: Atualizar EVOLUTION.md
Output Esperado: EVOLUTION.md atualizado.
```

## 4. Regras de Ouro

1.  **Imutabilidade de Papéis:** O GEMINI nunca conserta código. Ele apenas aponta o erro. O CODEX nunca opina sobre UX. O MISTRAL nunca inventa fatos.
2.  **Rastreabilidade:** Nenhuma linha de código entra no projeto sem um log correspondente em `docs/logs/`.
3.  **Fonte da Verdade:** Os arquivos na raiz (`*-PROJECT.md`, `*-STORAGE.md`) são a lei. Se o código discorda deles, o código está errado (ou a lei precisa ser emendada explicitamente pelo Orquestrador).
4.  **Idioma:** Toda a documentação e logs devem ser em **Português**.

