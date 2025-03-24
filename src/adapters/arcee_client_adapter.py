#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptador para o cliente Arcee

Este módulo implementa um adaptador que permite que o ArceeClient
seja utilizado através da interface LLMClient.
"""

from typing import Dict, List, Optional, Any
from src.interfaces.llm_client import LLMClient
from src.llm.providers.arcee_client import ArceeClient
from src.exceptions import ConfigurationError, LLMApiError


class ArceeClientAdapter(LLMClient):
    """
    Adaptador para o cliente Arcee
    
    Este adaptador implementa a interface LLMClient utilizando
    a implementação concreta do ArceeClient.
    """
    
    def __init__(self):
        """Inicializa o adaptador sem criar o cliente ainda"""
        self._client = None
        self._initialized = False
    
    def initialize(self, api_key: str, model: str = "auto") -> None:
        """
        Inicializa o cliente com a chave de API e configurações
        
        Args:
            api_key: Chave de API para o serviço LLM
            model: Modelo a ser utilizado, padrão é 'auto'
        
        Raises:
            ConfigurationError: Se a inicialização falhar
        """
        try:
            self._client = ArceeClient(api_key=api_key, model=model)
            self._initialized = True
        except ValueError as e:
            self._initialized = False
            raise ConfigurationError(f"Erro ao inicializar cliente Arcee: {str(e)}")
        except Exception as e:
            self._initialized = False
            raise ConfigurationError(f"Erro inesperado ao inicializar cliente Arcee: {str(e)}")
    
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
        if not self._initialized or self._client is None:
            raise ConfigurationError("Cliente Arcee não inicializado")
        
        # Aplica a instrução do sistema se fornecida
        msg_copy = messages.copy()
        if system_instruction and (not msg_copy or msg_copy[0].get("role") != "system"):
            msg_copy.insert(0, {"role": "system", "content": system_instruction})
        
        try:
            result = self._client.generate_content_chat(msg_copy, **kwargs)
            
            # Verifica se houve erro na resposta
            if "error" in result and result["error"]:
                raise LLMApiError(f"Erro na API da Arcee: {result['error']}")
            
            return result
        except Exception as e:
            if isinstance(e, LLMApiError):
                raise
            raise LLMApiError(f"Erro ao enviar mensagem para a Arcee: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo em uso
        
        Returns:
            Dict contendo informações como nome do modelo, 
            razão da seleção, tipo de tarefa, etc.
        """
        if not self._initialized or self._client is None:
            raise ConfigurationError("Cliente Arcee não inicializado")
        
        return {
            "model": self._client.model,
            "selected_model": None,  # Será preenchido após uma chamada à API
            "selection_reason": None,
            "task_type": None,
            "domain": None,
            "complexity": None,
            "available_models": self._client.get_available_models()
        }
    
    def is_initialized(self) -> bool:
        """
        Verifica se o cliente foi inicializado
        
        Returns:
            bool indicando se o cliente está pronto para uso
        """
        return self._initialized and self._client is not None 