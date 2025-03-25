#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para listar as listas de um quadro Trello usando MCP.run
"""

import subprocess
import json
import sys

# Configurações
TRELLO_TOKEN = 'ATTA990c61c1754403f36cbdd2e90697e8bef99785a0e72af0f3184a97f711472086074DFEF1'
TRELLO_BOARD_ID = 'js3cvo6W'
MCP_SESSION = 'mcpx/diegofornalha/szuUQ5DpbKxQqw8dHtyJR4VzigtpebrB.dAvoQb5AKtEPUl+bZ12fcTg6ov0ZpcBWA2t/jZXNuKY'

def listar_listas():
    """Listar as listas do quadro Trello"""
    print("Listando listas do quadro Trello...")
    
    # Parâmetros para o Trello
    params = json.dumps({
        "token": TRELLO_TOKEN,
        "board_id": TRELLO_BOARD_ID
    })
    
    # Comando para executar o MCP
    cmd = [
        "npx", "mcpx", 
        "run", "trello.board_get_lists", 
        "--json", params, 
        "--session", MCP_SESSION
    ]
    
    print(f"Executando: {' '.join(cmd)}")
    
    try:
        # Executar o comando
        resultado = subprocess.run(
            cmd, 
            check=True,
            capture_output=True,
            text=True
        )
        
        # Mostrar o resultado
        print("\nResultado obtido:")
        print(resultado.stdout)
        
        # Tentar processar como JSON
        try:
            listas = json.loads(resultado.stdout)
            print("\nListas encontradas:")
            if isinstance(listas, list):
                for i, lista in enumerate(listas):
                    print(f"{i+1}. {lista.get('name')} (ID: {lista.get('id')})")
        except json.JSONDecodeError:
            print("O resultado não pôde ser interpretado como JSON.")
            
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando: {e}")
        print(f"Saída: {e.stderr}")
        return 1
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(listar_listas()) 