#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para listar tarefas no Airtable

Este script conecta na API do Airtable e lista todas as tarefas
da tabela especificada, mostrando seus detalhes em formato legível.
"""

import requests
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Airtable a partir de variáveis de ambiente
config = {
    "api_key": os.getenv("AIRTABLE_API_KEY"),
    "base_id": os.getenv("AIRTABLE_BASE_ID"),
    "table_id": os.getenv("AIRTABLE_TABLE_ID")
}

def listar_tarefas_airtable():
    """Busca todas as tarefas no Airtable"""
    # Verifica se as variáveis de ambiente estão configuradas
    if not config["api_key"] or not config["base_id"] or not config["table_id"]:
        print("❌ Erro: Variáveis de ambiente AIRTABLE_API_KEY, AIRTABLE_BASE_ID e AIRTABLE_TABLE_ID não configuradas.")
        print("   Copie o arquivo .env.example para .env e configure as variáveis.")
        sys.exit(1)
    
    url = f"https://api.airtable.com/v0/{config['base_id']}/{config['table_id']}"
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    try:
        print("Conectando ao Airtable...")
        response = requests.get(url, headers=headers)
        
        # Verificar se a requisição foi bem-sucedida
        response.raise_for_status()
        
        # Retornar os dados em formato JSON
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"\nERRO: Falha na requisição à API do Airtable: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"\nERRO: Falha ao interpretar resposta da API: {response.text}")
        sys.exit(1)

def mostrar_tarefas(dados):
    """Exibe as tarefas formatadas"""
    print("\n=== TAREFAS NO AIRTABLE ===\n")
    
    if not dados.get("records") or len(dados["records"]) == 0:
        print("Nenhuma tarefa encontrada.")
        return
    
    for index, record in enumerate(dados["records"]):
        fields = record.get("fields", {})
        
        print(f"Tarefa #{index + 1} (ID: {record['id']})")
        print(f"Nome: {fields.get('Task', 'Sem nome')}")
        print(f"Status: {fields.get('Status', 'Não definido')}")
        
        if "Notes" in fields and fields["Notes"]:
            print(f"Descrição: {fields['Notes']}")
        
        if "Deadline" in fields and fields["Deadline"]:
            print(f"Data de Vencimento: {fields['Deadline']}")
        
        if "Owner" in fields and fields["Owner"]:
            print(f"Responsável: {fields['Owner']}")
        
        print(f"Criado em: {record.get('createdTime', 'Data desconhecida')}")
        print("----------------------------")
    
    print(f"Total de tarefas: {len(dados['records'])}")

def main():
    """Função principal"""
    try:
        dados = listar_tarefas_airtable()
        mostrar_tarefas(dados)
    except Exception as e:
        print(f"\nERRO não tratado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()