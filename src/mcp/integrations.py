#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integração com servidores MCP

Este módulo fornece integração com os servidores MCP configurados
no sistema, permitindo que o Arcee acesse as mesmas ferramentas
que o agente do Cursor.
"""

import os
import json
import subprocess
import requests
from typing import Dict, List, Any, Optional, Union

# Importa as exceções personalizadas
from src.exceptions import AirtableApiError, ConfigurationError, MCPServerError, VeyraxApiError, MCPError

# Importa a integração com Veyrax
from src.veyrax import VeyraxIntegration, VeyraxAdapter

class MCPIntegration:
    """
    Integração com servidores MCP configurados no sistema.
    
    Esta classe fornece métodos para interagir com servidores MCP (Multi-agent 
    Cognitive Protocol) configurados no sistema. Ela carrega a configuração dos 
    servidores a partir do arquivo ~/.cursor/mcp.json e permite listar, verificar 
    e iniciar servidores.
    
    Attributes:
        config_path (str): Caminho para o arquivo de configuração MCP
        servers (dict): Dicionário de servidores MCP disponíveis
    """
    
    def __init__(self):
        """
        Inicializa a integração MCP.
        
        Configura o caminho para o arquivo de configuração e carrega 
        os servidores disponíveis.
        """
        self.config_path = os.path.expanduser("~/.cursor/mcp.json")
        self.servers = {}
        self.load_servers()
    
    def load_servers(self):
        """
        Carrega os servidores MCP disponíveis a partir do arquivo de configuração.
        
        O arquivo de configuração deve estar no formato JSON e conter uma chave
        "mcpServers" com a configuração dos servidores.
        
        Raises:
            Exception: Se ocorrer um erro ao carregar o arquivo de configuração
        """
        try:
            # Verifica se o arquivo de configuração existe
            if not os.path.exists(self.config_path):
                print(f"Arquivo de configuração MCP não encontrado: {self.config_path}")
                return
            
            # Carrega a configuração
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Extrai os servidores
            if "mcpServers" in config:
                self.servers = config["mcpServers"]
                print(f"Servidores MCP carregados: {', '.join(self.servers.keys())}")
            else:
                print("Nenhum servidor MCP encontrado na configuração")
        
        except Exception as e:
            print(f"Erro ao carregar servidores MCP: {e}")
    
    def list_available_servers(self) -> List[str]:
        """
        Lista os servidores MCP disponíveis.
        
        Returns:
            List[str]: Lista com os nomes dos servidores disponíveis
        """
        return list(self.servers.keys())
    
    def has_server(self, server_name: str) -> bool:
        """
        Verifica se um servidor está disponível.
        
        Args:
            server_name (str): Nome do servidor a ser verificado
            
        Returns:
            bool: True se o servidor estiver disponível, False caso contrário
        """
        return server_name in self.servers
    
    def start_server(self, server_name: str) -> bool:
        """
        Inicia um servidor MCP
        
        Nota: Esta funcionalidade está implementada para uso futuro,
        mas não é utilizada na interface atual. Poderá ser útil quando
        implementarmos recursos para iniciar servidores MCP automaticamente
        a partir da interface de chat.
        
        Args:
            server_name (str): Nome do servidor a ser iniciado
            
        Returns:
            bool: True se o servidor foi iniciado com sucesso, False caso contrário
        """
        if not self.has_server(server_name):
            print(f"Servidor MCP não encontrado: {server_name}")
            return False
        
        try:
            # Obtém a configuração do servidor
            server_config = self.servers[server_name]
            
            # Prepara o comando
            command = [server_config["command"]] + server_config["args"]
            
            # Inicia o servidor
            subprocess.Popen(command, start_new_session=True)
            print(f"Servidor MCP iniciado: {server_name}")
            return True
        
        except Exception as e:
            print(f"Erro ao iniciar servidor MCP {server_name}: {e}")
            return False

# Integrações específicas para cada servidor MCP

class AirtableIntegration:
    """
    Integração com o serviço Airtable para gerenciamento de tarefas.
    
    Esta classe fornece métodos para criar e listar tarefas no Airtable,
    utilizando a API REST do serviço. É necessário configurar as credenciais
    de acesso através de variáveis de ambiente.
    
    Attributes:
        api_key (str): Chave de API do Airtable
        base_id (str): ID da base de dados
        table_id (str): ID da tabela de tarefas
    """
    
    def __init__(self):
        """
        Inicializa a integração com o Airtable.
        
        Carrega as credenciais a partir das variáveis de ambiente:
        - AIRTABLE_API_KEY: Chave de API do Airtable
        - AIRTABLE_BASE_ID: ID da base de dados
        - AIRTABLE_TABLE_ID: ID da tabela de tarefas
        """
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        self.table_id = os.getenv("AIRTABLE_TABLE_ID")
    
    def is_initialized(self) -> bool:
        """
        Verifica se as credenciais estão configuradas.
        
        Returns:
            bool: True se as credenciais estiverem configuradas, False caso contrário
        """
        return bool(self.api_key and self.base_id and self.table_id)
    
    def initialize(self, api_key: str, base_id: str, table_id: str) -> None:
        """
        Inicializa a integração com credenciais fornecidas diretamente.
        
        Args:
            api_key (str): Chave de API do Airtable
            base_id (str): ID da base de dados
            table_id (str): ID da tabela de tarefas
            
        Raises:
            ConfigurationError: Se algum parâmetro for inválido
        """
        if not api_key or not base_id or not table_id:
            missing = []
            if not api_key: missing.append("api_key")
            if not base_id: missing.append("base_id")
            if not table_id: missing.append("table_id")
            raise ConfigurationError(f"Parâmetros obrigatórios não fornecidos: {', '.join(missing)}")
        
        self.api_key = api_key
        self.base_id = base_id
        self.table_id = table_id
        
        print(f"Integração Airtable inicializada com base_id={self.base_id}, table_id={self.table_id}")
    
    def create_task(self, task_name: str, description: str = None, deadline: str = None, status: str = "Not started") -> Dict[str, Any]:
        """
        Cria uma nova tarefa no Airtable
        
        Args:
            task_name (str): Nome da tarefa
            description (str, optional): Descrição da tarefa
            deadline (str, optional): Data limite (YYYY-MM-DD)
            status (str, optional): Status da tarefa
            
        Returns:
            Dict[str, Any]: Resposta da API
            
        Raises:
            ConfigurationError: Se as credenciais do Airtable não estiverem configuradas
            AirtableApiError: Se ocorrer um erro na comunicação com a API do Airtable
        """
        # Verifica se as credenciais estão configuradas
        if not self.is_initialized():
            raise ConfigurationError("Credenciais do Airtable não configuradas", "AIRTABLE_API_KEY/BASE_ID/TABLE_ID")
        
        # Configura o payload
        payload = {
            "records": [
                {
                    "fields": {
                        "Task": task_name,
                        "Status": status
                    }
                }
            ],
            "typecast": True
        }
        
        # Adiciona campos opcionais
        if description:
            payload["records"][0]["fields"]["Notes"] = description
        
        if deadline:
            payload["records"][0]["fields"]["Deadline"] = deadline
        
        # Faz a requisição
        try:
            url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise AirtableApiError(f"Erro na comunicação com a API do Airtable: {str(e)}")
    
    def list_tasks(self) -> Dict[str, Any]:
        """
        Lista as tarefas do Airtable
        
        Returns:
            Dict[str, Any]: Lista de tarefas
            
        Raises:
            ConfigurationError: Se as credenciais do Airtable não estiverem configuradas
            AirtableApiError: Se ocorrer um erro na comunicação com a API do Airtable
        """
        # Verifica se as credenciais estão configuradas
        if not self.is_initialized():
            raise ConfigurationError("Credenciais do Airtable não configuradas", "AIRTABLE_API_KEY/BASE_ID/TABLE_ID")
        
        # Faz a requisição
        try:
            url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise AirtableApiError(f"Erro na comunicação com a API do Airtable: {str(e)}")
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Exclui uma tarefa do Airtable
        
        Args:
            task_id (str): ID da tarefa a ser excluída
        
        Returns:
            Dict[str, Any]: Resposta da API
            
        Raises:
            ConfigurationError: Se as credenciais do Airtable não estiverem configuradas
            AirtableApiError: Se ocorrer um erro na comunicação com a API do Airtable
        """
        # Verifica se as credenciais estão configuradas
        if not self.is_initialized():
            raise ConfigurationError("Credenciais do Airtable não configuradas", "AIRTABLE_API_KEY/BASE_ID/TABLE_ID")
        
        # Faz a requisição
        try:
            url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_id}/{task_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise AirtableApiError(f"Erro ao excluir tarefa: {str(e)}")
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza uma tarefa existente no Airtable
        
        Args:
            task_id (str): ID da tarefa a ser atualizada
            updates (Dict[str, Any]): Campos a serem atualizados
        
        Returns:
            Dict[str, Any]: Resposta da API
            
        Raises:
            ConfigurationError: Se as credenciais do Airtable não estiverem configuradas
            AirtableApiError: Se ocorrer um erro na comunicação com a API do Airtable
        """
        # Verifica se as credenciais estão configuradas
        if not self.is_initialized():
            raise ConfigurationError("Credenciais do Airtable não configuradas", "AIRTABLE_API_KEY/BASE_ID/TABLE_ID")
        
        # Prepara o payload
        payload = {
            "fields": {}
        }
        
        # Mapeia as chaves do dicionário updates para os campos do Airtable
        field_mapping = {
            "task_name": "Task",
            "description": "Notes", 
            "deadline": "Deadline",
            "status": "Status",
            "Task": "Task",
            "Notes": "Notes",
            "Deadline": "Deadline",
            "Status": "Status"
        }
        
        for key, value in updates.items():
            if key in field_mapping and value is not None:
                payload["fields"][field_mapping[key]] = value
        
        # Faz a requisição
        try:
            url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_id}/{task_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.patch(url, headers=headers, json=payload)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise AirtableApiError(f"Erro ao atualizar tarefa: {str(e)}")

class VeyraxMCPIntegration(MCPIntegration):
    """
    Integração do Veyrax com o protocolo MCP.
    """
    
    def __init__(self, veyrax_adapter=None, api_key=None, use_mock=False):
        """
        Inicializa a integração do Veyrax com MCP.
        
        Args:
            veyrax_adapter: Adaptador do Veyrax pré-configurado. Se não fornecido, cria um novo.
            api_key: Chave de API do Veyrax. Usada apenas se veyrax_adapter não for fornecido.
            use_mock: Se True, usa dados simulados em vez de fazer chamadas reais à API.
        """
        try:
            # Importa aqui para evitar dependência circular
            from src.veyrax.veyrax_adapter import VeyraxAdapter
            
            self.adapter = veyrax_adapter or VeyraxAdapter(api_key=api_key, use_mock=use_mock)
        except ImportError:
            raise ImportError("Veyrax não está disponível. Verifique se o pacote está instalado.")
        except Exception as e:
            raise VeyraxApiError(f"Erro na API do Veyrax: {str(e)}")
    
    def get_tools(self):
        """
        Implementação do método MCP get_tools para Veyrax.
        
        Returns:
            Dicionário contendo as ferramentas disponíveis no Veyrax.
        """
        try:
            return self.adapter.get_tools()
        except Exception as e:
            raise VeyraxApiError(f"Erro na API do Veyrax: {str(e)}")
    
    def execute_tool(self, tool_name: str, method_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ferramenta no Veyrax.
        
        Args:
            tool_name: Nome da ferramenta a ser executada.
            method_name: Nome do método a ser executado.
            parameters: Parâmetros para a execução do método.
            
        Returns:
            Resultado da execução da ferramenta.
            
        Raises:
            VeyraxApiError: Se ocorrer um erro durante a execução da ferramenta.
        """
        try:
            return self.adapter.execute_tool(tool_name, method_name, parameters)
        except Exception as e:
            raise VeyraxApiError(f"Erro ao executar ferramenta {tool_name}.{method_name} no Veyrax: {str(e)}")
    
    def tool_call(self, tool_name: str, method_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma chamada de ferramenta no Veyrax.
        
        Args:
            tool_name: Nome da ferramenta a ser executada.
            method_name: Nome do método a ser executado.
            parameters: Parâmetros para a execução do método.
            
        Returns:
            Resultado da execução da ferramenta.
            
        Raises:
            MCPError: Se ocorrer um erro durante a execução da ferramenta.
        """
        try:
            return self.adapter.execute_tool(tool_name, method_name, parameters)
        except Exception as e:
            raise MCPError(f"Erro ao executar ferramenta {tool_name}.{method_name} no Veyrax: {str(e)}")

# Exemplo de uso
if __name__ == "__main__":
    # Testa a integração MCP
    mcp_integration = MCPIntegration()
    servers = mcp_integration.list_available_servers()
    print(f"Servidores disponíveis: {servers}")
    
    # Testa a integração Airtable
    airtable = AirtableIntegration()
    tasks = airtable.list_tasks()
    print(f"Tarefas: {tasks}") 