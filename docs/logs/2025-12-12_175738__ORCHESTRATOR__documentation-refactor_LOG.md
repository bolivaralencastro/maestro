# ORCHESTRATOR — Log de Decisão Arquitetural (Processo)

**Timestamp:** 2025-12-12 17:57:38
**Responsável:** Orquestrador (Antigravity)

---

## Tópico: Refatoração Documental para Eficiência de Tokens

## 1. Contexto e Problema
Após análise das métricas de uso das CLIs (Gemini e Qwen) extraídas na auditoria de encerramento do MVP, identificou-se um consumo elevado de **Input Tokens** (>260k em uma sessão Qwen).

A causa raiz identificada é a estratégia de manter um `EVOLUTION.md` monolítico que serve simultaneamente como:
- Histórico completo (crescimento linear infinito).
- Status atual (snapshot).
- Backlog (planejamento).

Para cada ciclo de trabalho, as IAs precisam ler e processar esse arquivo grande, gerando custo e latência desnecessários.

## 2. Decisão Estratégica
Decidimos **desacoplar** a documentação viva do projeto em três artefatos especializados.

### Nova Estrutura Documental (`docs/`):

| Arquivo | Função | Característica | Público Alvo |
| :--- | :--- | :--- | :--- |
| **`EVOLUTION.md`** | Histórico Imutável e Lições | Cresce sempre, lido raramente. | MISTRAL (Historiador) |
| **`STATUS.md`** | Snapshot do Estado Atual | Curto, denso, atualizado a cada feature. | CODEX, GEMINI (Contexto técnico) |
| **`BACKLOG.md`** | Matriz de Prioridades | Vivo, reorganizável, guia o próximo passo. | ORCHESTRADOR (Planejamento) |

## 3. Benefícios Esperados
1.  **Eficiência:** Redução drástica do contexto de entrada para tarefas de codificação (CODEX precisará ler apenas `STATUS.md` e a tarefa, ignorando o histórico antigo).
2.  **Foco:** O `BACKLOG.md` permitirá uma visão mais clara e priorizada (matriz) do que uma lista linear no fim de um arquivo longo.
3.  **Organização:** Separação clara de responsabilidades.

## 4. Ação Imediata
Instruído o agente **MISTRAL** a realizar a migração dos dados do atual `EVOLUTION.md` para os novos arquivos `STATUS.md` e `BACKLOG.md`, limpando o original para manter apenas o histórico cronológico.
