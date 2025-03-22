#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface para serviços de gerenciamento de tarefas

Define a interface abstrata para integração com 
serviços de gerenciamento de tarefas (Airtable, etc).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union


class TaskService(ABC):
    """
    Interface para serviços de gerenciamento de tarefas
    
    Esta interface abstrai a comunicação com diferentes serviços 
    de gerenciamento de tarefas, permitindo trocar implementações 
    sem afetar o código cliente.
    """
    
    @abstractmethod
    def initialize(self, api_key: str, base_id: str, table_id: str) -> None:
        """
        Inicializa o serviço com as credenciais e configurações
        
        Args:
            api_key: Chave de API para o serviço
            base_id: ID da base de dados
            table_id: ID da tabela de tarefas
            
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
    def create_task(self, task_name: str, 
                    description: Optional[str] = None,
                    deadline: Optional[str] = None,
                    status: str = "Not started") -> Dict[str, Any]:
        """
        Cria uma nova tarefa
        
        Args:
            task_name: Nome da tarefa
            description: Descrição detalhada (opcional)
            deadline: Data limite no formato YYYY-MM-DD (opcional)
            status: Status inicial da tarefa
            
        Returns:
            Dicionário com informações da tarefa criada
            
        Raises:
            AirtableApiError: Se ocorrer erro na comunicação com a API
        """
        pass
    
    @abstractmethod
    def list_tasks(self, filter_by: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lista as tarefas existentes
        
        Args:
            filter_by: Dicionário com filtros a serem aplicados (opcional)
            
        Returns:
            Dicionário com as tarefas encontradas
            
        Raises:
            AirtableApiError: Se ocorrer erro na comunicação com a API
        """
        pass
    
    @abstractmethod
    def update_task(self, task_id: str, 
                    updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza uma tarefa existente
        
        Args:
            task_id: ID da tarefa a ser atualizada
            updates: Dicionário com os campos a serem atualizados
            
        Returns:
            Dicionário com as informações atualizadas da tarefa
            
        Raises:
            AirtableApiError: Se ocorrer erro na comunicação com a API
        """
        pass
    
    @abstractmethod
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Remove uma tarefa existente
        
        Args:
            task_id: ID da tarefa a ser removida
            
        Returns:
            Dicionário com informações da operação
            
        Raises:
            AirtableApiError: Se ocorrer erro na comunicação com a API
        """
        pass 