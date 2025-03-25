#!/bin/bash

# Script para iniciar o servidor MCP-Trello em segundo plano

# Define boardId como parâmetro opcional
BOARD_ID="$1"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Iniciando Servidor MCP-Trello em segundo plano ===${NC}"

# Determina o diretório raiz do projeto
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
SERVIDOR_DIR="$PROJECT_ROOT/mcp-server-trello"

# Verifica se o servidor já está rodando
if pgrep -f "node build/index.js" > /dev/null; then
    echo -e "${GREEN}✅ Servidor MCP-Trello já está rodando!${NC}"
    exit 0
fi

# Vai para o diretório do servidor
if [ ! -d "$SERVIDOR_DIR" ]; then
    echo -e "${RED}❌ Erro: Diretório do servidor MCP-Trello não encontrado${NC}"
    echo "Caminho buscado: $SERVIDOR_DIR"
    exit 1
fi

# Cria diretório de logs se não existir
mkdir -p "$SERVIDOR_DIR/logs"

# Informa sobre o boardId
if [ -n "$BOARD_ID" ]; then
    echo -e "Usando boardId: ${GREEN}$BOARD_ID${NC}"
else
    echo "Usando boardId do arquivo .env"
fi

# Inicia o servidor em segundo plano
echo "Iniciando o servidor em segundo plano..."
# Se boardId foi fornecido, sobrescreve a variável de ambiente
if [ -n "$BOARD_ID" ]; then
    (cd "$SERVIDOR_DIR" && TRELLO_BOARD_ID="$BOARD_ID" npm start > logs/trello-server.log 2>&1 &)
else
    (cd "$SERVIDOR_DIR" && npm start > logs/trello-server.log 2>&1 &)
fi

# Aguarda um pouco para verificar se iniciou corretamente
sleep 2

# Verifica se o servidor está rodando
if pgrep -f "node build/index.js" > /dev/null; then
    echo -e "${GREEN}✅ Servidor MCP-Trello iniciado com sucesso em segundo plano!${NC}"
    echo "Log disponível em: $SERVIDOR_DIR/logs/trello-server.log"
    
    # Mostrar o PID para referência
    PID=$(pgrep -f "node build/index.js")
    echo -e "PID: ${GREEN}$PID${NC}"
    echo "Para encerrar o servidor: kill $PID"
else
    echo -e "${RED}❌ Falha ao iniciar o servidor em segundo plano${NC}"
    echo "Verifique o log para mais detalhes: $SERVIDOR_DIR/logs/trello-server.log"
    exit 1
fi 