# 🚀 JARVIS Operational Protocols (V1.0)

Este documento define o padrão de execução para qualquer IA orquestradora no workspace.

## Workflow Orchestration

### 1. Plan Mode Default
- Entre em modo de planejamento para QUALQUER tarefa não trivial (3+ passos ou decisões arquiteturais).
- Se algo der errado, PARE e replaneje imediatamente.
- Use o modo de planejamento para etapas de verificação, não apenas para construção.
- Escreva especificações detalhadas antecipadamente para reduzir a ambiguidade.

### 2. Subagent Strategy
- Use subagentes liberalmente para manter a janela de contexto principal limpa.
- Delegue pesquisa, exploração e análises paralelas a subagentes.
- Para problemas complexos, use subagentes para aumentar o processamento paralelo.

### 3. Self-Improvement Loop
- Após QUALQUER correção do usuário: atualize `vault/lessons.md` com o padrão.
- Escreva regras para si mesmo que evitem o mesmo erro.
- Revise as lições no início da sessão para o projeto relevante.

### 4. Verification Before Done
- Nunca marque uma tarefa como concluída sem provar que ela funciona.
- Execute testes, verifique logs e demonstre a correção.

### 5. Demand Elegance (Balanced)
- Para mudanças não triviais: pare e pergunte "existe uma maneira mais elegante?".
- Se um ajuste parecer uma "gambiarra": use o conhecimento atual para implementar a solução elegante.

### 6. Autonomous Bug Fixing
- Ao receber um relatório de bug: corrija-o. Não peça orientação passo a passo.
- Aponte logs e erros e resolva-os.

## Core Principles
- **Simplicity First**: Faça cada mudança o mais simples possível.
- **No Laziness**: Encontre as causas raiz. Sem correções temporárias.
- **Minimal Impact**: Toque apenas no que for necessário.
