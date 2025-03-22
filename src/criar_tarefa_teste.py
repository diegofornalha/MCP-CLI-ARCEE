#!/usr/bin/env python3

"""
Script para testar a criação de tarefas no Airtable
"""

import requests
import json
import sys
import datetime
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def criar_tarefa_airtable(nome_tarefa, descricao=None, vencimento=None, status="Not started"):
    """
    Cria uma tarefa no Airtable
    
    Args:
        nome_tarefa (str): Nome da tarefa
        descricao (str, optional): Descrição detalhada
        vencimento (str, optional): Data de vencimento (YYYY-MM-DD)
        status (str, optional): Status da tarefa
    
    Returns:
        dict: Resposta da API com os detalhes da tarefa criada
    """
    # Configuração do Airtable a partir de variáveis de ambiente
    base_id = os.getenv("AIRTABLE_BASE_ID")
    table_name = "Tasks"
    api_key = os.getenv("AIRTABLE_API_KEY")
    
    # Verifica se as variáveis de ambiente estão configuradas
    if not base_id or not api_key:
        print("❌ Erro: Variáveis de ambiente AIRTABLE_BASE_ID e AIRTABLE_API_KEY não configuradas.")
        print("   Copie o arquivo .env.example para .env e configure as variáveis.")
        return {"error": "Configuração ausente"}
    
    # Configura dados da tarefa
    task_data = {
        "records": [
            {
                "fields": {
                    "Task": nome_tarefa,
                    "Status": status
                }
            }
        ],
        "typecast": True
    }
    
    # Adiciona campos opcionais se fornecidos
    if descricao:
        task_data["records"][0]["fields"]["Notes"] = descricao
    
    if vencimento:
        task_data["records"][0]["fields"]["Deadline"] = vencimento
    else:
        # Usa a data atual como padrão
        task_data["records"][0]["fields"]["Deadline"] = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Faz a requisição para a API
    try:
        print(f"Criando tarefa: {nome_tarefa}")
        print(f"Dados: {json.dumps(task_data, indent=2)}")
        
        response = requests.post(
            f"https://api.airtable.com/v0/{base_id}/{table_name}",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=task_data
        )
        
        # Verifica se a requisição foi bem-sucedida
        response.raise_for_status()
        resultado = response.json()
        
        # Mostra resultado
        print("\n✅ Tarefa criada com sucesso!")
        print(f"ID: {resultado['records'][0]['id']}")
        print(f"Criada em: {resultado['records'][0]['createdTime']}")
        print(f"Campos: {json.dumps(resultado['records'][0]['fields'], indent=2)}")
        
        return resultado
    
    except Exception as e:
        print(f"❌ Erro ao criar tarefa: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Se argumentos forem fornecidos na linha de comando, usa-os
    if len(sys.argv) > 1:
        nome = sys.argv[1]
        descricao = sys.argv[2] if len(sys.argv) > 2 else f"Tarefa criada via script de teste: {nome}"
        vencimento = sys.argv[3] if len(sys.argv) > 3 else None
        status = sys.argv[4] if len(sys.argv) > 4 else "Not started"
    else:
        # Valores padrão
        nome = f"Tarefa de teste - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        descricao = "Tarefa criada pelo script de teste em Python"
        vencimento = None
        status = "Not started"
    
    # Cria a tarefa
    criar_tarefa_airtable(nome, descricao, vencimento, status)