#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fábrica de Serviços

Este módulo implementa uma fábrica para criar instâncias das diferentes
interfaces de serviço utilizando os adaptadores apropriados.
"""

import os
from typing import Dict, Any, Optional, Type
from src.exceptions import ConfigurationError

# Interfaces
from src.interfaces.llm_client import LLMClient
from src.interfaces.mcp_service import MCPService
from src.interfaces.task_service import TaskService
from src.interfaces.rest_service import RestService
from src.interfaces.file_service import FileService

# Adaptadores
from src.adapters.arcee_client_adapter import ArceeClientAdapter
from src.adapters.mcp_service_adapter import MCPServiceAdapter
from src.adapters.task_service_adapter import TaskServiceAdapter
from src.adapters.rest_service_adapter import RequestsRestAdapter
from src.adapters.file_service_adapter import LocalFileAdapter

# Constantes para tipos de serviço
LLM_CLIENT_ARCEE = "arcee"
MCP_SERVICE_DEFAULT = "default"
TASK_SERVICE_AIRTABLE = "airtable"
REST_SERVICE_REQUESTS = "requests"
FILE_SERVICE_LOCAL = "local"

from src.mcp.integrations import MCPIntegration, AirtableIntegration


class ServiceFactory:
    """
    Fábrica para criar instâncias de serviços
    
    Esta classe fornece métodos estáticos para criar diferentes
    tipos de serviços, abstraindo a implementação concreta.
    """
    
    @staticmethod
    def create_llm_client(client_type: str = LLM_CLIENT_ARCEE, 
                          api_key: Optional[str] = None,
                          model: str = "auto") -> LLMClient:
        """
        Cria uma instância de cliente LLM
        
        Args:
            client_type: Tipo do cliente ("arcee" por padrão)
            api_key: Chave API (usa variável de ambiente se None)
            model: Modelo a ser utilizado (padrão "auto")
        
        Returns:
            Instância de LLMClient inicializada
        
        Raises:
            ConfigurationError: Se o tipo de cliente for inválido
                               ou ocorrer erro na inicialização
        """
        if client_type.lower() == LLM_CLIENT_ARCEE:
            # Tenta obter API key de variável de ambiente se não fornecida
            api_key = api_key or os.getenv("ARCEE_API_KEY")
            
            # Cria e inicializa o adaptador
            client = ArceeClientAdapter()
            client.initialize(api_key=api_key, model=model)
            return client
        else:
            raise ConfigurationError(f"Tipo de cliente LLM não suportado: {client_type}")
    
    @staticmethod
    def create_mcp_service() -> MCPService:
        """
        Cria e configura um serviço MCP
        
        Returns:
            MCPService: Instância do serviço MCP
        """
        mcp_implementation = MCPIntegration()
        adapter = MCPServiceAdapter(mcp_implementation)
        
        # Imprime informações de depuração
        print("MCPService criado pela factory")
        
        return adapter
    
    @staticmethod
    def create_task_service() -> TaskService:
        """
        Cria e configura um serviço de gerenciamento de tarefas
        
        Returns:
            TaskService: Instância do serviço de tarefas
        """
        airtable_implementation = AirtableIntegration()
        adapter = TaskServiceAdapter(airtable_implementation)
        
        # Imprime informações de depuração
        print("TaskService criado pela factory")
        
        return adapter
    
    @staticmethod
    def create_rest_service(service_type: str = REST_SERVICE_REQUESTS,
                           base_url: Optional[str] = None,
                           api_key: Optional[str] = None,
                           headers: Optional[Dict[str, str]] = None) -> RestService:
        """
        Cria uma instância de serviço REST
        
        Args:
            service_type: Tipo do serviço ("requests" por padrão)
            base_url: URL base para as requisições
            api_key: Chave API (opcional)
            headers: Cabeçalhos padrão para requisições (opcional)
        
        Returns:
            Instância de RestService inicializada
        
        Raises:
            ConfigurationError: Se o tipo de serviço for inválido
                               ou ocorrer erro na inicialização
        """
        if service_type.lower() == REST_SERVICE_REQUESTS:
            # Cria o adaptador
            service = RequestsRestAdapter()
            
            # Inicializa somente se base_url for fornecido
            if base_url:
                service.initialize(base_url=base_url, api_key=api_key, headers=headers)
                
            return service
        else:
            raise ConfigurationError(f"Tipo de serviço REST não suportado: {service_type}")
    
    @staticmethod
    def create_file_service(service_type: str = FILE_SERVICE_LOCAL,
                           base_path: Optional[str] = None,
                           credentials: Optional[Dict[str, Any]] = None) -> FileService:
        """
        Cria uma instância de serviço de arquivos
        
        Args:
            service_type: Tipo do serviço ("local" por padrão)
            base_path: Caminho base para operações de arquivo (opcional)
            credentials: Credenciais para acesso (para sistemas em nuvem)
        
        Returns:
            Instância de FileService inicializada
        
        Raises:
            ConfigurationError: Se o tipo de serviço for inválido
                               ou ocorrer erro na inicialização
        """
        if service_type.lower() == FILE_SERVICE_LOCAL:
            # Cria o adaptador
            service = LocalFileAdapter()
            
            # Inicializa com o caminho base (opcional)
            service.initialize(base_path=base_path, credentials=credentials)
                
            return service
        else:
            raise ConfigurationError(f"Tipo de serviço de arquivos não suportado: {service_type}")
    
    @staticmethod
    def create_services_from_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria múltiplos serviços a partir de uma configuração
        
        Args:
            config: Dicionário com configurações para os serviços
        
        Returns:
            Dicionário com os serviços inicializados
        
        Raises:
            ConfigurationError: Se ocorrer erro na inicialização de algum serviço
        """
        services = {}
        
        # Cria cliente LLM se configurado
        if "llm" in config:
            llm_config = config["llm"]
            services["llm_client"] = ServiceFactory.create_llm_client(
                client_type=llm_config.get("type", LLM_CLIENT_ARCEE),
                api_key=llm_config.get("api_key"),
                model=llm_config.get("model", "auto")
            )
        
        # Cria serviço MCP se configurado
        if "mcp" in config:
            mcp_config = config["mcp"]
            services["mcp_service"] = ServiceFactory.create_mcp_service()
        
        # Cria serviço de tarefas se configurado
        if "task" in config:
            task_config = config["task"]
            services["task_service"] = ServiceFactory.create_task_service()
            
        # Cria serviço REST se configurado
        if "rest" in config:
            rest_config = config["rest"]
            services["rest_service"] = ServiceFactory.create_rest_service(
                service_type=rest_config.get("type", REST_SERVICE_REQUESTS),
                base_url=rest_config.get("base_url"),
                api_key=rest_config.get("api_key"),
                headers=rest_config.get("headers")
            )
            
        # Cria serviço de arquivos se configurado
        if "file" in config:
            file_config = config["file"]
            services["file_service"] = ServiceFactory.create_file_service(
                service_type=file_config.get("type", FILE_SERVICE_LOCAL),
                base_path=file_config.get("base_path"),
                credentials=file_config.get("credentials")
            )
        
        return services 