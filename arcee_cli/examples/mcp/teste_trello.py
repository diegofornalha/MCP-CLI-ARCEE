#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste de integração da API Trello com MCP.run
"""

import os
import sys
import json
import subprocess
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Obtém a sessão MCP.run
MCP_SESSION = os.getenv("MCP_SESSION_ID")
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")

if not MCP_SESSION:
    print("❌ Erro: Variável MCP_SESSION_ID não configurada no arquivo .env")
    sys.exit(1)

if not TRELLO_API_KEY:
    print("❌ Erro: Variável TRELLO_API_KEY não configurada no arquivo .env")
    sys.exit(1)

if not TRELLO_TOKEN:
    print("⚠️ Aviso: Variável TRELLO_TOKEN não configurada no arquivo .env")
    print("   Somente métodos que não requerem autenticação funcionarão")

def testar_mcp_ferramentas():
    """Verifica se as ferramentas MCP estão disponíveis"""
    try:
        print("Verificando ferramentas MCP disponíveis...")
        cmd = f"npx mcpx tools --session {MCP_SESSION}"
        resultado = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        
        # Verifica se 'trello' está nas ferramentas disponíveis
        if "trello" in resultado.stdout:
            print("✅ Ferramenta 'trello' encontrada no MCP.run")
            return True
        else:
            print("❌ Ferramenta 'trello' NÃO encontrada no MCP.run")
            print("   Instale a ferramenta em: https://www.mcp.run")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao listar ferramentas MCP: {e}")
        print(f"Saída: {e.stderr}")
        return False

def testar_trello_auth():
    """Testa a autenticação Trello via MCP.run"""
    try:
        print("\nTestando API de autorização do Trello...")
        cmd = f"npx mcpx run trello.auth_get_url --session {MCP_SESSION}"
        resultado = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        
        # Tenta extrair URL de autenticação
        saida = resultado.stdout
        if "https://trello.com/1/authorize" in saida:
            print("✅ API de autorização Trello funcionando")
            return True
        else:
            print("❌ API de autorização Trello falhou")
            print(f"Saída: {saida}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao testar API de autorização: {e}")
        print(f"Saída: {e.stderr}")
        return False

def testar_trello_boards(token=None):
    """Testa a listagem de quadros se token disponível"""
    if not token:
        print("\n⚠️ Token não fornecido, pulando teste de listagem de quadros")
        return False
    
    try:
        print("\nTestando listagem de quadros Trello...")
        params = json.dumps({"token": token})
        cmd = f"npx mcpx run trello.board_list --json '{params}' --session {MCP_SESSION}"
        resultado = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        
        # Verificar se a resposta parece ser uma lista de quadros
        saida = resultado.stdout
        if "id" in saida and "name" in saida:
            print("✅ Listagem de quadros funcionando")
            return True
        else:
            print("❌ Listagem de quadros falhou")
            print(f"Saída: {saida}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao listar quadros: {e}")
        print(f"Saída: {e.stderr}")
        return False

def main():
    """Função principal de teste"""
    print("=== Teste de Integração Trello com MCP.run ===\n")
    
    # Verifica se as ferramentas estão disponíveis
    if not testar_mcp_ferramentas():
        print("\n❌ Teste falhou: Ferramentas MCP não configuradas corretamente")
        return 1
    
    # Testa a API de autorização
    if not testar_trello_auth():
        print("\n❌ Teste falhou: API de autorização não funcionou")
        return 1
    
    # Testa a listagem de quadros se token disponível
    if TRELLO_TOKEN:
        testar_trello_boards(TRELLO_TOKEN)
    
    print("\n=== Teste Concluído ===")
    print("✅ A integração Trello com MCP.run está configurada corretamente")
    return 0

if __name__ == "__main__":
    sys.exit(main())
