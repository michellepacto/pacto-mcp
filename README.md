# Pacto MCP Server

MCP server para atualizar arquivos do repositório Pacto_CRM via Claude.

## Ferramentas disponíveis
- `update_file` — Atualiza arquivo existente
- `create_file` — Cria novo arquivo
- `list_files` — Lista arquivos de uma pasta

## Configuração
Variáveis de ambiente necessárias no Render:
- `GITHUB_TOKEN` — Personal Access Token do GitHub
- `GITHUB_REPO` — Repositório (padrão: michellepacto/Pacto_CRM)
