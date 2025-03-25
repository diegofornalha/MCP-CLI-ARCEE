#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar um quadro no Trello via API
"""

import os
import sys
import requests
import dotenv
from rich import print

# Carrega variáveis de ambiente do arquivo .env
dotenv.load_dotenv()

# Obtém as credenciais do ambiente
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")

if not TRELLO_API_KEY or not TRELLO_TOKEN:
    print("[bold red]❌ Erro: Credenciais do Trello não encontradas no arquivo .env[/bold red]")
    print("Por favor, configure TRELLO_API_KEY e TRELLO_TOKEN no arquivo .env")
    sys.exit(1)

def create_board(name, description=None):
    """
    Cria um novo quadro no Trello
    
    Args:
        name: Nome do quadro
        description: Descrição do quadro (opcional)
        
    Returns:
        Dados do quadro criado ou None em caso de erro
    """
    url = "https://api.trello.com/1/boards/"
    
    # Parâmetros da requisição
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "name": name,
        "defaultLists": "false"  # Não criar listas padrão
    }
    
    if description:
        params["desc"] = description
    
    print(f"[bold blue]🔄 Criando quadro '{name}'...[/bold blue]")
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()  # Lança exceção se a requisição falhar
        
        board_data = response.json()
        print(f"[bold green]✅ Quadro criado com sucesso![/bold green]")
        print(f"[bold]ID do quadro:[/bold] {board_data['id']}")
        print(f"[bold]URL do quadro:[/bold] {board_data['url']}")
        
        return board_data
    except requests.exceptions.RequestException as e:
        print(f"[bold red]❌ Erro ao criar quadro: {str(e)}[/bold red]")
        if hasattr(e, 'response') and e.response:
            print(f"Resposta: {e.response.text}")
        return None

def create_list(board_id, name):
    """
    Cria uma nova lista em um quadro
    
    Args:
        board_id: ID do quadro
        name: Nome da lista
        
    Returns:
        Dados da lista criada ou None em caso de erro
    """
    url = "https://api.trello.com/1/lists"
    
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "name": name,
        "idBoard": board_id
    }
    
    print(f"[bold blue]🔄 Criando lista '{name}'...[/bold blue]")
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        list_data = response.json()
        print(f"[bold green]✅ Lista '{name}' criada com sucesso![/bold green]")
        print(f"[bold]ID da lista:[/bold] {list_data['id']}")
        
        return list_data
    except requests.exceptions.RequestException as e:
        print(f"[bold red]❌ Erro ao criar lista: {str(e)}[/bold red]")
        if hasattr(e, 'response') and e.response:
            print(f"Resposta: {e.response.text}")
        return None

if __name__ == "__main__":
    # Verifica se foi fornecido o nome do quadro
    if len(sys.argv) < 2:
        print("Uso: python create_trello_board.py <nome_do_quadro> [descrição]")
        sys.exit(1)
    
    board_name = sys.argv[1]
    board_description = sys.argv[2] if len(sys.argv) >= 3 else None
    
    # Cria o quadro
    board = create_board(board_name, board_description)
    
    if board:
        # Pergunta se quer criar listas padrão
        create_default_lists = input("Deseja criar listas padrão (A Fazer, Em Andamento, Concluído)? (s/n): ").lower() == 's'
        
        if create_default_lists:
            board_id = board['id']
            create_list(board_id, "A Fazer")
            create_list(board_id, "Em Andamento")
            create_list(board_id, "Concluído")
            
            print("\n[bold green]✅ Quadro configurado com sucesso![/bold green]")
            print(f"[bold]Para usar este quadro no servidor MCP-Trello, adicione a seguinte linha ao arquivo .env:[/bold]")
            print(f"TRELLO_BOARD_ID={board['id']}") 