#!/bin/bash

# Script para instalar o serviço MCP SSE Client como um serviço systemd

# Verifica se está sendo executado como root
if [ "$EUID" -ne 0 ]; then
  echo "Este script precisa ser executado como root (sudo)."
  exit 1
fi

# Configurações
SERVICO="mcp-sse-client"
USUARIO=$(logname || echo "$SUDO_USER")
DIR_ATUAL=$(pwd)
VENV_PATH=$(which python | sed 's/\/bin\/python$//')
SCRIPT_PATH="$DIR_ATUAL/arcee_cli/examples/mcp/mcp_sse_app.py"
SSE_URL=$(grep MCP_SSE_URL .env | cut -d '=' -f2)

# Verifica se o arquivo do serviço existe
if [ ! -f "$DIR_ATUAL/arcee_cli/examples/mcp/mcp_sse_service.service" ]; then
  echo "❌ Erro: Arquivo de serviço não encontrado."
  exit 1
fi

# Verifica se o script Python existe
if [ ! -f "$SCRIPT_PATH" ]; then
  echo "❌ Erro: Script Python não encontrado em: $SCRIPT_PATH"
  exit 1
fi

# Verifica se URL SSE está configurada
if [ -z "$SSE_URL" ]; then
  echo "❌ Erro: URL SSE não encontrada no arquivo .env"
  exit 1
fi

echo "=== Instalando Serviço MCP SSE Client ==="
echo "Usuário: $USUARIO"
echo "Diretório: $DIR_ATUAL"
echo "Ambiente Python: $VENV_PATH"
echo "Script: $SCRIPT_PATH"

# Cria o arquivo de serviço
cat > /etc/systemd/system/$SERVICO.service << EOF
[Unit]
Description=MCP.run SSE Client Service
After=network.target

[Service]
Type=simple
User=$USUARIO
WorkingDirectory=$DIR_ATUAL
ExecStart=$VENV_PATH/bin/python $SCRIPT_PATH
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=MCP_SSE_URL=$SSE_URL
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Recarrega o systemd para reconhecer o novo serviço
systemctl daemon-reload

# Habilita o serviço para iniciar com o sistema
systemctl enable $SERVICO.service

# Inicia o serviço
systemctl start $SERVICO.service

# Verifica status
echo ""
echo "=== Status do Serviço ==="
systemctl status $SERVICO.service

echo ""
echo "✅ Serviço instalado e iniciado com sucesso!"
echo ""
echo "Comandos úteis:"
echo "- Verificar status: sudo systemctl status $SERVICO"
echo "- Ver logs: sudo journalctl -u $SERVICO -f"
echo "- Parar serviço: sudo systemctl stop $SERVICO"
echo "- Iniciar serviço: sudo systemctl start $SERVICO"
echo "- Desabilitar inicialização automática: sudo systemctl disable $SERVICO" 