#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface para serviços MCP (Multi-Cloud Processing)

Define a interface abstrata para integração com 
serviços MCP de diferentes provedores.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union


class MCPService(ABC):
    """
    Interface para serviços MCP
    
    Esta interface abstrai a comunicação com diferentes serviços MCP,
    permitindo trocar implementações sem afetar o código cliente.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Inicializa o serviço MCP
        
        Raises:
            ConfigurationError: Se a inicialização falhar
        """
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Verifica se o serviço foi inicializado
        
        Returns:
            bool indicando se o serviço está pronto para uso
        """
        pass
    
    @abstractmethod
    def get_available_servers(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de servidores MCP disponíveis
        
        Returns:
            Lista de dicionários contendo informações dos servidores
        
        Raises:
            MCPApiError: Se ocorrer erro na comunicação com a API
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass 