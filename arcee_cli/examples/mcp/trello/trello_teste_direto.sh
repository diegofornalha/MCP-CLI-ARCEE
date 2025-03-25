#!/bin/bash

# Carregar variáveis do .env
source .env

echo "=== Teste direto da API Trello com MCP ==="
echo "Usando sessão: $MCP_SESSION_ID"

# Listar quadros do Trello
echo -e "\nListando seus quadros do Trello...\n"
mcpx run trello.board_list --json "{\"token\":\"$TRELLO_TOKEN\"}" --session "$MCP_SESSION_ID"

# Testar quadro específico
echo -e "\n\n=== Detalhes do quadro '$TRELLO_BOARD_NAME' ($TRELLO_BOARD_ID) ===\n"
mcpx run trello.board_get --json "{\"token\":\"$TRELLO_TOKEN\",\"board_id\":\"$TRELLO_BOARD_ID\"}" --session "$MCP_SESSION_ID"

# Listar as listas do quadro
echo -e "\n\n=== Listas do quadro '$TRELLO_BOARD_NAME' ===\n"
mcpx run trello.board_get_lists --json "{\"token\":\"$TRELLO_TOKEN\",\"board_id\":\"$TRELLO_BOARD_ID\"}" --session "$MCP_SESSION_ID"

echo -e "\n✅ Teste concluído" 