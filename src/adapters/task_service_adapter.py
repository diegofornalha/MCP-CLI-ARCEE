#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptador para o serviço de tarefas do Airtable

Este módulo implementa um adaptador que permite que a integração
com o Airtable seja utilizada através da interface TaskService.
"""

from typing import Dict, List, Optional, Any, Union
from src.interfaces.task_service import TaskService
from src.exceptions import NotImplementedError, ConfigurationError, AirtableApiError


class TaskServiceAdapter(TaskService):
    """
    Adaptador para serviços de gerenciamento de tarefas
    
    Esta classe implementa a interface TaskService e adapta para
    a implementação específica do serviço (ex: Airtable).
    """
    
    def __init__(self, service_implementation):
        """
        Inicializa o adaptador
        
        Args:
            service_implementation: Implementação concreta do serviço
        """
        self.service = service_implementation
        self._initialized = False
        
        # Verifica que métodos a implementação suporta
        self.supports_delete = hasattr(self.service, 'delete_task')
        self.supports_update = hasattr(self.service, 'update_task')
        self.supports_get = hasattr(self.service, 'get_task')
        
        # Registro de debug
        print(f"TaskServiceAdapter inicializado. Suporte a operações: "
              f"delete={self.supports_delete}, update={self.supports_update}, "
              f"get={self.supports_get}")
        
        # Tenta inicializar automaticamente se a implementação já estiver pronta
        if hasattr(self.service, "is_initialized") and self.service.is_initialized():
            self._initialized = True
            print("TaskServiceAdapter: serviço já estava inicializado")
    
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
        try:
            if hasattr(self.service, "initialize"):
                self.service.initialize(api_key, base_id, table_id)
                self._initialized = True
                print("TaskServiceAdapter: serviço inicializado com sucesso")
            else:
                raise ConfigurationError("O serviço não suporta inicialização manual")
        except Exception as e:
            print(f"Erro ao inicializar serviço de tarefas: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """
        Verifica se o serviço foi inicializado
        
        Returns:
            bool indicando se o serviço está pronto para uso
        """
        # Se o serviço possui seu próprio método is_initialized, usamos ele
        if hasattr(self.service, "is_initialized"):
            return self.service.is_initialized()
        # Caso contrário, retornamos nosso status interno
        return self._initialized
    
    def create_task(self, task_name: str, description: str = None, 
                  deadline: str = None, status: str = "Not started") -> Dict[str, Any]:
        """
        Cria uma nova tarefa
        
        Args:
            task_name (str): Nome da tarefa
            description (str, optional): Descrição da tarefa
            deadline (str, optional): Data limite no formato YYYY-MM-DD
            status (str, optional): Status inicial da tarefa
            
        Returns:
            Dict[str, Any]: Dados da tarefa criada
            
        Raises:
            ConfigurationError: Se o serviço não estiver configurado corretamente
            APIError: Se ocorrer um erro na API do serviço
        """
        if not self.is_initialized():
            raise ConfigurationError("O serviço de tarefas não foi inicializado")
            
        try:
            result = self.service.create_task(task_name, description, deadline, status)
            return result
        except Exception as e:
            # Relança a exceção, mas com informações adicionais
            print(f"Erro ao criar tarefa: {e}")
            raise
    
    def list_tasks(self) -> Dict[str, Any]:
        """
        Lista as tarefas disponíveis
        
        Returns:
            Dict[str, Any]: Lista com as tarefas
            
        Raises:
            ConfigurationError: Se o serviço não estiver configurado corretamente
            APIError: Se ocorrer um erro na API do serviço
        """
        try:
            result = self.service.list_tasks()
            return result
        except Exception as e:
            print(f"Erro ao listar tarefas: {e}")
            raise
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Exclui uma tarefa pelo ID
        
        Args:
            task_id (str): ID da tarefa a ser excluída
            
        Returns:
            Dict[str, Any]: Resultado da operação
            
        Raises:
            NotImplementedError: Se a implementação não suportar esta operação
            ConfigurationError: Se o serviço não estiver configurado corretamente
            APIError: Se ocorrer um erro na API do serviço
        """
        if not self.supports_delete:
            error_msg = "A implementação não suporta exclusão de tarefas"
            print(f"Erro: {error_msg}")
            raise NotImplementedError(error_msg, "delete_task")
        
        # Validação básica do ID
        if not task_id or task_id.lower() in ["id_da_tarefa", "task_id", "id1", "id2", "id3"]:
            raise ValueError(f"ID de tarefa inválido: '{task_id}'")
        
        try:
            print(f"Tentando excluir tarefa com ID: {task_id}")
            result = self.service.delete_task(task_id)
            print(f"Tarefa excluída com sucesso: {task_id}")
            return result
        except Exception as e:
            print(f"Erro ao excluir tarefa: {e}")
            raise
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza uma tarefa existente
        
        Args:
            task_id (str): ID da tarefa a ser atualizada
            updates (Dict[str, Any]): Dados a serem atualizados
            
        Returns:
            Dict[str, Any]: Dados da tarefa atualizada
            
        Raises:
            NotImplementedError: Se a implementação não suportar esta operação
            ConfigurationError: Se o serviço não estiver configurado corretamente
            APIError: Se ocorrer um erro na API do serviço
        """
        if not self.supports_update:
            error_msg = "A implementação não suporta atualização de tarefas"
            print(f"Erro: {error_msg}")
            raise NotImplementedError(error_msg, "update_task")
        
        try:
            result = self.service.update_task(task_id, updates)
            return result
        except Exception as e:
            print(f"Erro ao atualizar tarefa: {e}")
            raise
    
    def get_task_by_id(self, task_id: str) -> Dict[str, Any]:
        """
        Obtém uma tarefa pelo ID
        
        Args:
            task_id (str): ID da tarefa
            
        Returns:
            Dict[str, Any]: Dados da tarefa
            
        Raises:
            NotImplementedError: Se a implementação não suportar esta operação
            ConfigurationError: Se o serviço não estiver configurado corretamente
            APIError: Se ocorrer um erro na API do serviço
        """
        if not self.supports_get:
            # Se não há suporte para get_task direto, tentamos simular com list_tasks
            # Isso é uma solução de "fallback" para implementações limitadas
            try:
                print(f"Buscando tarefa com ID {task_id} através de list_tasks")
                all_tasks = self.service.list_tasks()
                tasks = all_tasks.get("records", [])
                
                for task in tasks:
                    if task.get("id") == task_id:
                        print(f"Tarefa encontrada: {task}")
                        return task
                
                print(f"Tarefa com ID {task_id} não encontrada")
                raise ValueError(f"Tarefa com ID {task_id} não encontrada")
            
            except Exception as e:
                print(f"Erro ao buscar tarefa: {e}")
                raise
        else:
            try:
                result = self.service.get_task(task_id)
                return result
            except Exception as e:
                print(f"Erro ao buscar tarefa: {e}")
                raise 