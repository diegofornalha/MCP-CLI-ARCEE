#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptador para serviços REST

Implementa a interface RestService usando a biblioteca requests.
"""

import requests
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse

from src.interfaces.rest_service import RestService
from src.exceptions import RestApiError, ConfigurationError


class RequestsRestAdapter(RestService):
    """
    Adaptador REST baseado na biblioteca requests
    
    Esta implementação da interface RestService utiliza a biblioteca
    requests para realizar requisições HTTP.
    """
    
    def __init__(self):
        """Inicializa o adaptador com valores padrão"""
        self.base_url = None
        self.api_key = None
        self.default_headers = {}
        self.session = requests.Session()
        self._initialized = False
    
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
        if not base_url:
            raise ConfigurationError("URL base não pode ser vazia")
        
        # Validar formato da URL
        try:
            parsed_url = urlparse(base_url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise ValueError("URL inválida")
        except Exception as e:
            raise ConfigurationError(f"URL base inválida: {str(e)}")
        
        # Garantir que a URL base termina com '/'
        if not base_url.endswith('/'):
            base_url += '/'
            
        self.base_url = base_url
        self.api_key = api_key
        
        # Configurar cabeçalhos padrão
        self.default_headers = headers or {}
        if api_key:
            # Adicionar cabeçalho de autenticação, se não existir outro método
            if 'Authorization' not in self.default_headers:
                self.default_headers['Authorization'] = f'Bearer {api_key}'
        
        # Criar nova sessão
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)
        
        self._initialized = True
    
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
        self._check_initialized()
        
        url = self.build_url(endpoint)
        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            return self._process_response(response)
        except requests.exceptions.HTTPError as e:
            raise RestApiError(
                f"Erro HTTP na requisição GET: {str(e)}", 
                status_code=response.status_code if 'response' in locals() else None,
                response=response.json() if 'response' in locals() else None
            )
        except requests.exceptions.RequestException as e:
            raise RestApiError(f"Erro na requisição GET: {str(e)}")
    
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
        self._check_initialized()
        
        url = self.build_url(endpoint)
        try:
            response = self.session.post(url, data=data, json=json_data, headers=headers)
            response.raise_for_status()
            return self._process_response(response)
        except requests.exceptions.HTTPError as e:
            raise RestApiError(
                f"Erro HTTP na requisição POST: {str(e)}", 
                status_code=response.status_code if 'response' in locals() else None,
                response=response.json() if 'response' in locals() else None
            )
        except requests.exceptions.RequestException as e:
            raise RestApiError(f"Erro na requisição POST: {str(e)}")
    
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
        self._check_initialized()
        
        url = self.build_url(endpoint)
        try:
            response = self.session.put(url, data=data, json=json_data, headers=headers)
            response.raise_for_status()
            return self._process_response(response)
        except requests.exceptions.HTTPError as e:
            raise RestApiError(
                f"Erro HTTP na requisição PUT: {str(e)}", 
                status_code=response.status_code if 'response' in locals() else None,
                response=response.json() if 'response' in locals() else None
            )
        except requests.exceptions.RequestException as e:
            raise RestApiError(f"Erro na requisição PUT: {str(e)}")
    
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
        self._check_initialized()
        
        url = self.build_url(endpoint)
        try:
            response = self.session.delete(url, params=params, headers=headers)
            response.raise_for_status()
            return self._process_response(response)
        except requests.exceptions.HTTPError as e:
            raise RestApiError(
                f"Erro HTTP na requisição DELETE: {str(e)}", 
                status_code=response.status_code if 'response' in locals() else None,
                response=response.json() if 'response' in locals() else None
            )
        except requests.exceptions.RequestException as e:
            raise RestApiError(f"Erro na requisição DELETE: {str(e)}")
    
    def is_initialized(self) -> bool:
        """
        Verifica se o serviço foi inicializado
        
        Returns:
            bool indicando se o serviço está pronto para uso
        """
        return self._initialized
    
    def build_url(self, endpoint: str) -> str:
        """
        Constrói uma URL completa a partir do endpoint
        
        Args:
            endpoint: Caminho do endpoint
            
        Returns:
            URL completa para o endpoint
        """
        if endpoint.startswith('http://') or endpoint.startswith('https://'):
            return endpoint
        
        # Remover barra inicial do endpoint se existir para evitar duplicação
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
            
        return urljoin(self.base_url, endpoint)
    
    def _check_initialized(self) -> None:
        """
        Verifica se o serviço foi inicializado, lançando exceção se não foi
        
        Raises:
            ConfigurationError: Se o serviço não foi inicializado
        """
        if not self._initialized:
            raise ConfigurationError("Serviço REST não foi inicializado")
    
    def _process_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Processa a resposta da requisição
        
        Args:
            response: Objeto de resposta do requests
            
        Returns:
            Dicionário com os dados processados
            
        Raises:
            RestApiError: Se ocorrer erro no processamento da resposta
        """
        try:
            if response.content and response.headers.get('Content-Type', '').startswith('application/json'):
                return response.json()
            else:
                return {
                    'status_code': response.status_code,
                    'content': response.text,
                    'headers': dict(response.headers)
                }
        except ValueError as e:
            # Erro ao converter resposta para JSON
            return {
                'status_code': response.status_code,
                'content': response.text,
                'error': f"Erro ao processar resposta JSON: {str(e)}",
                'headers': dict(response.headers)
            } 