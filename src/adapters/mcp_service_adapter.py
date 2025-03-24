#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptador para o serviço MCP

Este módulo implementa um adaptador que permite que a integração
com MCP seja utilizada através da interface MCPService.
"""

from typing import Dict, List, Optional, Any
from src.interfaces.mcp_service import MCPService
from src.exceptions import ConfigurationError, MCPServiceError


class MCPServiceAdapter(MCPService):
    """
    Adaptador para o serviço MCP
    
    Este adaptador implementa a interface MCPService utilizando
    a implementação concreta da integração MCP.
    """
    
    def __init__(self, service_implementation=None):
        """
        Inicializa o adaptador
        
        Args:
            service_implementation: Implementação concreta do serviço MCP (opcional)
        """
        self._integration = service_implementation
        self._initialized = self._integration is not None
        self._available_servers = []
        self._current_server = None
        
        # Se uma implementação foi fornecida, lista servidores disponíveis
        if self._initialized:
            try:
                self._available_servers = self._integration.list_available_servers()
                if self._available_servers:
                    # Seleciona o primeiro disponível como padrão
                    self._current_server = self._available_servers[0]
                print(f"MCPServiceAdapter inicializado com implementação fornecida. "
                      f"Servidores disponíveis: {', '.join(self._available_servers)}")
            except Exception as e:
                print(f"Aviso: Erro ao listar servidores na inicialização: {e}")
        
        # Inicialização automática se nenhuma implementação foi fornecida
        elif service_implementation is None:
            try:
                self.initialize()
            except:
                # Ignora erros na inicialização automática
                pass
    
    def initialize(self, api_key: Optional[str] = None, server: Optional[str] = None) -> None:
        """
        Inicializa o serviço MCP com chave API e configurações
        
        Args:
            api_key: Chave API para o serviço MCP (pode ser None)
            server: Servidor específico para conectar (pode ser None)
        
        Raises:
            ConfigurationError: Se a inicialização falhar
        """
        try:
            # Se já temos uma implementação, apenas configura
            if self._integration is not None:
                # Configura API key se fornecida
                if api_key and hasattr(self._integration, 'api_key'):
                    self._integration.api_key = api_key
                
                # Lista servidores disponíveis
                self._available_servers = self._integration.list_available_servers()
                
                # Seleciona servidor específico se fornecido
                if server and server in self._available_servers:
                    self._current_server = server
                elif self._available_servers and not self._current_server:
                    # Seleciona o primeiro disponível se nenhum já estiver selecionado
                    self._current_server = self._available_servers[0]
            else:
                # Importação aqui para evitar dependência circular
                from src.mcp.integrations import MCPIntegration
                
                self._integration = MCPIntegration()
                
                # Configura API key se fornecida
                if api_key and hasattr(self._integration, 'api_key'):
                    self._integration.api_key = api_key
                
                # Lista servidores disponíveis
                self._available_servers = self._integration.list_available_servers()
                
                # Seleciona servidor específico se fornecido
                if server and server in self._available_servers:
                    self._current_server = server
                elif self._available_servers:
                    # Seleciona o primeiro disponível
                    self._current_server = self._available_servers[0]
            
            self._initialized = True
            print(f"MCPService inicializado. Servidor atual: {self._current_server}")
        except Exception as e:
            self._initialized = False
            raise ConfigurationError(f"Erro ao inicializar serviço MCP: {str(e)}")
    
    def list_available_servers(self) -> List[str]:
        """
        Lista os servidores MCP disponíveis
        
        Returns:
            Lista de nomes de servidores disponíveis
        
        Raises:
            ConfigurationError: Se o serviço não estiver inicializado
            MCPServiceError: Se ocorrer erro ao listar servidores
        """
        if not self._initialized or self._integration is None:
            raise ConfigurationError("Serviço MCP não inicializado")
        
        try:
            # Atualiza a lista de servidores disponíveis
            self._available_servers = self._integration.list_available_servers()
            return self._available_servers
        except Exception as e:
            raise MCPServiceError(f"Erro ao listar servidores MCP: {str(e)}")
    
    def get_available_servers(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de servidores MCP disponíveis com informações detalhadas
        
        Returns:
            Lista de dicionários contendo informações dos servidores
        
        Raises:
            MCPApiError: Se ocorrer erro na comunicação com a API
        """
        if not self._initialized or self._integration is None:
            raise ConfigurationError("Serviço MCP não inicializado")
        
        try:
            # Primeiro obtém a lista de nomes de servidores
            server_names = self.list_available_servers()
            
            # Depois, obtém informações detalhadas para cada servidor
            servers_info = []
            for name in server_names:
                info = self.get_server_status(name)
                servers_info.append(info)
            
            return servers_info
        except Exception as e:
            raise MCPServiceError(f"Erro ao obter servidores disponíveis: {str(e)}")
    
    def get_server_info(self, server_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém informações sobre um servidor específico
        
        Args:
            server_name: Nome do servidor (usa o atual se None)
        
        Returns:
            Dict contendo informações do servidor
        
        Raises:
            ConfigurationError: Se o serviço não estiver inicializado
            MCPServiceError: Se ocorrer erro ao obter informações do servidor
        """
        if not self._initialized or self._integration is None:
            raise ConfigurationError("Serviço MCP não inicializado")
        
        try:
            server = server_name or self._current_server
            
            if not server:
                raise MCPServiceError("Nenhum servidor selecionado ou disponível")
            
            # Verifica se a implementação suporta get_server_info
            if hasattr(self._integration, 'get_server_info'):
                return self._integration.get_server_info(server)
            else:
                # Informações básicas se não suportar
                return {
                    "name": server,
                    "status": "online" if server in self._available_servers else "unknown"
                }
        except Exception as e:
            if isinstance(e, MCPServiceError):
                raise
            raise MCPServiceError(f"Erro ao obter informações do servidor: {str(e)}")
    
    def select_server(self, server_name: str) -> bool:
        """
        Seleciona um servidor específico para uso
        
        Args:
            server_name: Nome do servidor a ser selecionado
        
        Returns:
            bool indicando se a seleção foi bem-sucedida
        
        Raises:
            ConfigurationError: Se o serviço não estiver inicializado
            MCPServiceError: Se o servidor especificado não existir
        """
        if not self._initialized or self._integration is None:
            raise ConfigurationError("Serviço MCP não inicializado")
        
        try:
            # Atualiza a lista de servidores disponíveis
            self._available_servers = self._integration.list_available_servers()
            
            if server_name not in self._available_servers:
                raise MCPServiceError(f"Servidor '{server_name}' não disponível")
            
            self._current_server = server_name
            return True
        except Exception as e:
            if isinstance(e, MCPServiceError):
                raise
            raise MCPServiceError(f"Erro ao selecionar servidor: {str(e)}")
    
    def get_current_server(self) -> Optional[str]:
        """
        Retorna o servidor atualmente selecionado
        
        Returns:
            Nome do servidor atual ou None se nenhum estiver selecionado
        
        Raises:
            ConfigurationError: Se o serviço não estiver inicializado
        """
        if not self._initialized or self._integration is None:
            raise ConfigurationError("Serviço MCP não inicializado")
        
        return self._current_server
    
    def execute_query(self, query: str, server_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa uma consulta no servidor MCP
        
        Args:
            query: Consulta a ser executada
            server_name: Nome do servidor (usa o atual se None)
        
        Returns:
            Dict contendo resultado da consulta
        
        Raises:
            ConfigurationError: Se o serviço não estiver inicializado
            MCPServiceError: Se ocorrer erro na execução da consulta
        """
        if not self._initialized or self._integration is None:
            raise ConfigurationError("Serviço MCP não inicializado")
        
        try:
            server = server_name or self._current_server
            
            if not server:
                raise MCPServiceError("Nenhum servidor selecionado ou disponível")
            
            # Verifica se a implementação suporta execute_query
            if hasattr(self._integration, 'execute_query'):
                return self._integration.execute_query(query, server)
            else:
                raise MCPServiceError("Execução de consultas não implementada")
        except Exception as e:
            if isinstance(e, MCPServiceError):
                raise
            raise MCPServiceError(f"Erro ao executar consulta: {str(e)}")
    
    def is_initialized(self) -> bool:
        """
        Verifica se o serviço foi inicializado
        
        Returns:
            bool indicando se o serviço está pronto para uso
        """
        return self._initialized and self._integration is not None
    
    def start_server(self, server_name: str) -> Dict[str, Any]:
        """
        Inicia um servidor MCP
        
        Args:
            server_name: Nome do servidor a ser iniciado
        
        Returns:
            Dicionário com informações do servidor iniciado
            
        Raises:
            MCPApiError: Se ocorrer erro ao iniciar o servidor
        """
        if not self._initialized or self._integration is None:
            raise ConfigurationError("Serviço MCP não inicializado")
        
        try:
            # Verifica se a implementação suporta start_server
            if hasattr(self._integration, 'start_server'):
                result = self._integration.start_server(server_name)
                
                # Atualiza a lista de servidores disponíveis após iniciar
                self._available_servers = self._integration.list_available_servers()
                
                return result
            else:
                # Implementação padrão se não existir na integração
                if server_name in self._available_servers:
                    return {
                        "name": server_name,
                        "status": "running",
                        "message": "Servidor já está em execução"
                    }
                else:
                    raise MCPServiceError(f"Servidor '{server_name}' não encontrado")
        except Exception as e:
            if isinstance(e, MCPServiceError):
                raise
            raise MCPServiceError(f"Erro ao iniciar servidor: {str(e)}")
    
    def stop_server(self, server_name: str) -> Dict[str, Any]:
        """
        Para um servidor MCP
        
        Args:
            server_name: Nome do servidor a ser parado
            
        Returns:
            Dicionário com informações do servidor parado
            
        Raises:
            MCPApiError: Se ocorrer erro ao parar o servidor
        """
        if not self._initialized or self._integration is None:
            raise ConfigurationError("Serviço MCP não inicializado")
        
        try:
            # Verifica se a implementação suporta stop_server
            if hasattr(self._integration, 'stop_server'):
                result = self._integration.stop_server(server_name)
                
                # Atualiza a lista de servidores disponíveis após parar
                self._available_servers = self._integration.list_available_servers()
                
                return result
            else:
                # Implementação padrão se não existir na integração
                if server_name in self._available_servers:
                    return {
                        "name": server_name,
                        "status": "stopped",
                        "message": "Operação não suportada pela implementação atual"
                    }
                else:
                    raise MCPServiceError(f"Servidor '{server_name}' não encontrado")
        except Exception as e:
            if isinstance(e, MCPServiceError):
                raise
            raise MCPServiceError(f"Erro ao parar servidor: {str(e)}")
    
    def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """
        Obtém o status de um servidor MCP
        
        Args:
            server_name: Nome do servidor
            
        Returns:
            Dicionário com informações de status do servidor
            
        Raises:
            MCPApiError: Se ocorrer erro ao obter o status
        """
        if not self._initialized or self._integration is None:
            raise ConfigurationError("Serviço MCP não inicializado")
        
        try:
            # Verifica se a implementação suporta get_server_status
            if hasattr(self._integration, 'get_server_status'):
                return self._integration.get_server_status(server_name)
            else:
                # Implementação padrão se não existir na integração
                if server_name in self._available_servers:
                    return {
                        "name": server_name,
                        "status": "running",
                        "type": "mcp",
                        "message": "Status básico - implementação limitada"
                    }
                else:
                    raise MCPServiceError(f"Servidor '{server_name}' não encontrado")
        except Exception as e:
            if isinstance(e, MCPServiceError):
                raise
            raise MCPServiceError(f"Erro ao obter status do servidor: {str(e)}") 