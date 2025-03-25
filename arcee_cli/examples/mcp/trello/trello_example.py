#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemplo de uso do cliente Trello via MCP.
"""

import os
import sys
import dotenv
import json
from typing import Dict, Any

# Adiciona o caminho raiz do projeto ao PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.insert(0, project_root)

# Carrega variáveis de ambiente
dotenv.load_dotenv()

from arcee_cli.tools.mcp.trello.trello_client import TrelloClient

def exibir_listas(listas):
    """Exibe as listas formatadas"""
    print(f"\nListas no quadro '{os.getenv('TRELLO_BOARD_NAME', 'TesteToken')}' (total: {len(listas)}):")
    for i, lista in enumerate(listas, 1):
        print(f"{i}. {lista.get('name')} (ID: {lista.get('id')})")
        
def exibir_cartoes(cartoes, nome_lista):
    """Exibe os cartões formatados"""
    print(f"\nCartões na lista '{nome_lista}' (total: {len(cartoes)}):")
    if not cartoes:
        print("  Nenhum cartão encontrado.")
        return
        
    for i, cartao in enumerate(cartoes, 1):
        print(f"{i}. {cartao.get('name')}")
        if cartao.get('desc'):
            print(f"   Descrição: {cartao.get('desc')}")

def main():
    """Função principal do exemplo"""
    print("=== Exemplo de Uso do Cliente Trello via MCP ===")
    
    try:
        # Inicializa o cliente Trello
        cliente = TrelloClient()
        print(f"✅ Cliente Trello inicializado com sucesso")
        print(f"ID do quadro: {cliente.board_id}")
        
        # Lista todas as listas do quadro
        print("\nObtendo listas do quadro...")
        listas = cliente.get_lists()
        exibir_listas(listas)
        
        if listas:
            # Escolhe a primeira lista para exibir os cartões
            primeira_lista = listas[0]
            print(f"\nObtendo cartões da lista '{primeira_lista['name']}'...")
            cartoes = cliente.get_cards_by_list(primeira_lista['id'])
            exibir_cartoes(cartoes, primeira_lista['name'])
            
            # Cria um novo cartão na primeira lista
            print("\nCriando novo cartão...")
            novo_cartao = cliente.add_card(
                primeira_lista['id'],
                f"Tarefa criada em {import_datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
                "Este cartão foi criado automaticamente pelo script de exemplo"
            )
            
            if "error" not in novo_cartao:
                print(f"✅ Cartão criado com sucesso: {novo_cartao.get('name')}")
            else:
                print(f"❌ Erro ao criar cartão: {novo_cartao.get('error')}")
            
        # Obtém os cartões atribuídos ao usuário
        print("\nObtendo seus cartões...")
        meus_cartoes = cliente.get_my_cards()
        print(f"Você tem {len(meus_cartoes)} cartões atribuídos a você.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1
        
    print("\n✅ Exemplo concluído com sucesso!")
    return 0

if __name__ == "__main__":
    # Importa datetime aqui para evitar erro na referência do exemplo
    import datetime as import_datetime
    sys.exit(main()) 