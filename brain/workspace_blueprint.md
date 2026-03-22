# 🗺️ JARVIS Workspace Blueprint (V1.0)

Este documento define a racionalidade por trás da organização de arquivos e diretórios do Ecossistema JARVIS, servindo de base para as auditorias de eficiência.

## 🏛️ Estrutura de Diretórios (Pátios)

### 1. Projetos Ativos (Core)
- **JARVIS**: Infraestrutura central, orquestração e inteligência (Engine).
- **arte_**: Operação de licitações, matching e BI.
- **wappi**: Gateway de WhatsApp e automação de leads.

### 2. Pátios em Avaliação / Monitoramento
- **whatsapp**: Pátio de monitoramento direto de mensagens (Ativo).
- **global_window**: [A Definir pela CEO]

## 📄 Scripts e Integrações Estáticas

Alguns scripts operam de forma autônoma ou via CLI, não sendo detectados por `import` tradicional. Devem ser ignorados pela auditoria de orfandade:

- **integrations/notebooklm_client.py**: Cliente de integração RAG (Ativo).

## ⚖️ Regras de Governança de Eficiência

1. **Exceções de Importação**: Arquivos na pasta `engine/integrations/` e `engine/skills/` são frequentemente estáticos e não devem ser deletados sem auditoria manual.
2. **Ciclo de Inatividade**: Projetos sem commits há mais de 60 dias devem ser movidos para uma pasta `/archive` antes de qualquer deleção definitiva.
3. **Registro Obrigatório**: Todo novo diretório de projeto deve ser adicionado ao `engine/config/projects.json`.
