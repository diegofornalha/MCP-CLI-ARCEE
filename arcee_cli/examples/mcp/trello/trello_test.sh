#!/bin/bash

# Carregar variáveis do .env
source .env

# Usar sessão MCP existente
echo "Usando sessão MCP existente..."
SESSION_ID=$MCP_SESSION_ID

if [ -z "$SESSION_ID" ]; then
  echo "❌ Nenhuma sessão MCP encontrada no arquivo .env"
  echo "Gerando nova sessão MCP..."
  RESP=$(npx --yes -p @dylibso/mcpx@latest gen-session 2>&1)
  SESSION_ID=$(echo "$RESP" | grep "Session:" | cut -d' ' -f2)
  
  if [ -z "$SESSION_ID" ]; then
    echo "❌ Falha ao obter sessão MCP"
    exit 1
  fi
fi

echo "✅ Sessão MCP: $SESSION_ID"

# Verificar ferramentas disponíveis
echo -e "\nVerificando ferramentas MCP disponíveis..."
TOOLS=$(mcpx tools --session "$SESSION_ID" 2>&1)

if echo "$TOOLS" | grep -i trello > /dev/null; then
  echo "✅ Ferramenta Trello encontrada"
else
  echo "❌ Ferramenta Trello NÃO encontrada. Instale-a em https://www.mcp.run"
  exit 1
fi

# Testar a API - Listar quadros
echo -e "\nTestando API Trello - Listando quadros..."
mcpx run trello.board_list --json "{\"token\":\"$TRELLO_TOKEN\"}" --session "$SESSION_ID"

echo -e "\n✅ Teste concluído" 