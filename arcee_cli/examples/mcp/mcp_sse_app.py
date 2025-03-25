#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicação cliente SSE para MCP.run.

Esta aplicação conecta ao endpoint SSE do MCP.run com as credenciais fornecidas
e processa os eventos recebidos em tempo real.
"""

import sys
import os
import json
import dotenv
from typing import Dict, Any, cast

# Carrega variáveis de ambiente do arquivo .env
dotenv.load_dotenv()

# Importação do cliente SSE do pacote arcee_cli
from arcee_cli.infrastructure.mcp import MCPRunSSEClient, Evento

# Obtém a URL SSE do MCP.run das variáveis de ambiente
SSE_URL = os.getenv("MCP_SSE_URL")
if not SSE_URL:
    print("❌ Erro: Variável de ambiente MCP_SSE_URL não configurada no arquivo .env")
    sys.exit(1)

# Garantindo que SSE_URL é uma string para satisfazer o tipo
# Como já verificamos que não é None, podemos fazer o cast para str
SSE_URL = cast(str, SSE_URL)


def processar_evento(evento: Evento) -> None:
    """
    Processa um evento recebido do MCP.run
    
    Args:
        evento: Evento recebido via SSE
    """
    print(f"\n--- Novo Evento [{evento.event_type}] ---")
    
    # Tenta processar como JSON
    json_data = evento.json
    if json_data:
        # Formata o JSON para melhor visualização
        formatted_json = json.dumps(json_data, ensure_ascii=False, indent=2)
        print(f"Dados (JSON):\n{formatted_json}")
        
        # Extrai informações específicas se disponíveis
        if isinstance(json_data, dict):
            if "type" in json_data:
                print(f"Tipo de Mensagem: {json_data['type']}")
            if "message" in json_data:
                print(f"Mensagem: {json_data['message']}")
    else:
        # Imprime os dados brutos se não for JSON
        print(f"Dados (Raw): {evento.data}")
    
    print("----------------------------")


def main():
    """Função principal da aplicação"""
    print(f"=== Cliente SSE MCP.run ===")
    print(f"Conectando ao endpoint: {SSE_URL}")
    
    # Cria o cliente SSE com a URL fornecida
    cliente = MCPRunSSEClient(SSE_URL)
    
    # Inicia a conexão
    if not cliente.iniciar():
        print("❌ Falha ao iniciar o cliente SSE")
        return 1
    
    print("✅ Cliente SSE iniciado com sucesso")
    print("\nRecebendo eventos em tempo real...")
    print("(Pressione Ctrl+C para encerrar)")
    
    try:
        # Loop contínuo para processar eventos
        cliente.processar_eventos_loop(processar_evento)
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante processamento: {e}")
    finally:
        # Encerra o cliente
        print("Encerrando cliente SSE...")
        cliente.parar()
    
    print("Conexão encerrada")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 