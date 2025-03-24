#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface para serviços REST genéricos

Define a interface abstrata para comunicação com serviços REST,
independente do provedor específico.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse


class RestService(ABC):
    """
    Interface para serviços REST
    
    Esta interface abstrai a comunicação com diferentes serviços REST,
    permitindo implementações específicas para cada provedor.
    """
    
    @abstractmethod
    def initialize(self, base_url: str, api_key: Optional[str] = None, 
                  headers: Optional[Dict[str, str]] = None) -> None:
        """
        Inicializa o serviço REST com URL base e autenticação
        
        Args:
            base_url: URL base do serviço REST
            api_key: Chave de API para autenticação (opcional)
            headers: Cabeçalhos padrão para requisições (opcional)
            
        Raises:
            ConfigurationError: Se a inicialização falhar
        """
        pass
    
    @abstractmethod
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Realiza uma requisição GET
        
        Args:
            endpoint: Caminho do endpoint (será anexado à URL base)
            params: Parâmetros para a consulta (opcional)
            headers: Cabeçalhos específicos para esta requisição (opcional)
            
        Returns:
            Dicionário com a resposta da requisição
            
        Raises:
            RestApiError: Se ocorrer erro na comunicação com a API
        """
        pass
    
    @abstractmethod
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             json_data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Realiza uma requisição POST
        
        Args:
            endpoint: Caminho do endpoint (será anexado à URL base)
            data: Dados para enviar como form-data (opcional)
            json_data: Dados para enviar como JSON no corpo (opcional)
            headers: Cabeçalhos específicos para esta requisição (opcional)
            
        Returns:
            Dicionário com a resposta da requisição
            
        Raises:
            RestApiError: Se ocorrer erro na comunicação com a API
        """
        pass
    
    @abstractmethod
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Realiza uma requisição PUT
        
        Args:
            endpoint: Caminho do endpoint (será anexado à URL base)
            data: Dados para enviar como form-data (opcional)
            json_data: Dados para enviar como JSON no corpo (opcional)
            headers: Cabeçalhos específicos para esta requisição (opcional)
            
        Returns:
            Dicionário com a resposta da requisição
            
        Raises:
            RestApiError: Se ocorrer erro na comunicação com a API
        """
        pass
    
    @abstractmethod
    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
               headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Realiza uma requisição DELETE
        
        Args:
            endpoint: Caminho do endpoint (será anexado à URL base)
            params: Parâmetros para a consulta (opcional)
            headers: Cabeçalhos específicos para esta requisição (opcional)
            
        Returns:
            Dicionário com a resposta da requisição
            
        Raises:
            RestApiError: Se ocorrer erro na comunicação com a API
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
    def build_url(self, endpoint: str) -> str:
        """
        Constrói uma URL completa a partir do endpoint
        
        Args:
            endpoint: Caminho do endpoint
            
        Returns:
            URL completa para o endpoint
        """
        pass 