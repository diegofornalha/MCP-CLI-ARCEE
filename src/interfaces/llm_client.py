#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface para clientes de modelos de linguagem (LLM)

Define a interface abstrata para integração com diferentes 
provedores de modelos de linguagem (Arcee, OpenAI, etc).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union


class LLMClient(ABC):
    """
    Interface para clientes de modelos de linguagem
    
    Esta interface abstrai a comunicação com diferentes LLMs,
    permitindo trocar implementações sem afetar o código cliente.
    """
    
    @abstractmethod
    def initialize(self, api_key: str, model: str = "auto") -> None:
        """
        Inicializa o cliente com a chave de API e configurações
        
        Args:
            api_key: Chave de API para o serviço LLM
            model: Modelo a ser utilizado, padrão é 'auto'
        
        Raises:
            ConfigurationError: Se a inicialização falhar
        """
        pass
    
    @abstractmethod
    def send_message(self, messages: List[Dict[str, str]], 
                     system_instruction: Optional[str] = None,
                     stream: bool = False,
                     **kwargs) -> Dict[str, Any]:
        """
        Envia uma mensagem para o modelo de linguagem
        
        Args:
            messages: Lista de mensagens no formato {role: str, content: str}
            system_instruction: Instrução do sistema (opcional)
            stream: Indica se a resposta deve ser transmitida em stream
            **kwargs: Argumentos adicionais específicos da implementação
        
        Returns:
            Dict contendo a resposta do modelo e metadados
        
        Raises:
            LLMApiError: Se ocorrer erro na comunicação com a API
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo em uso
        
        Returns:
            Dict contendo informações como nome do modelo, 
            razão da seleção, tipo de tarefa, etc.
        """
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Verifica se o cliente foi inicializado
        
        Returns:
            bool indicando se o cliente está pronto para uso
        """
        pass 