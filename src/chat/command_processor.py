#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de processamento de comandos do chat

Este módulo fornece a classe CommandProcessor para gerenciar 
o processamento de comandos especiais embutidos nas mensagens 
do chat, como criação e listagem de tarefas no Airtable.
"""

import re
from src.exceptions import CommandProcessingError, ConfigurationError, AirtableApiError

class CommandProcessor:
    """Processa comandos especiais no chat"""
    
    def __init__(self, airtable_service):
        """
        Inicializa o processador de comandos
        
        Args:
            airtable_service: Serviço de integração com Airtable
        """
        self.airtable_service = airtable_service
    
    def process_commands(self, text):
        """
        Processa todos os comandos especiais no texto
        
        Args:
            text (str): Texto que pode conter comandos especiais
            
        Returns:
            str: Texto processado com os resultados dos comandos
        """
        processed_text = text
        processed_text = self.process_create_task_command(processed_text)
        processed_text = self.process_list_tasks_command(processed_text)
        return processed_text
    
    def extract_task_parameters(self, match):
        """
        Extrai e valida parâmetros de uma tarefa a partir de um match de regex
        
        Args:
            match: Match object da regex
            
        Returns:
            dict: Dicionário com os parâmetros da tarefa
        """
        return {
            "task_name": match.group(1).strip(),
            "description": match.group(2).strip() if match.group(2).strip() else None,
            "deadline": match.group(3).strip() if match.group(3).strip() else None,
            "status": match.group(4).strip() if match.group(4).strip() else "Not started"
        }
    
    def process_create_task_command(self, text):
        """
        Processa comandos de criação de tarefas no texto
        
        Args:
            text (str): Texto que pode conter comandos de criação de tarefas
            
        Returns:
            str: Texto processado com os resultados dos comandos
            
        Raises:
            CommandProcessingError: Se ocorrer um erro no processamento dos comandos
        """
        processed_text = text
        
        # Expressão regular que captura 4 grupos separados por "|":
        # 1. Nome da tarefa
        # 2. Descrição (opcional)
        # 3. Data limite (opcional)
        # 4. Status (opcional)
        # Exemplo: [[AIRTABLE_CREATE_TASK: Minha Tarefa | Descrição | 2023-12-31 | Em andamento]]
        create_task_pattern = r"\[\[AIRTABLE_CREATE_TASK: ([^|]+)\|([^|]*)\|([^|]*)\|([^]]*)\]\]"
        
        # Processamos continuamente enquanto houver padrões para substituir
        # Isso permite múltiplos comandos de criação de tarefas em um único texto
        while re.search(create_task_pattern, processed_text):
            match = re.search(create_task_pattern, processed_text)
            if match:
                # Extrai parâmetros
                params = self.extract_task_parameters(match)
                command = match.group(0)
                
                try:
                    # Cria a tarefa na API do Airtable
                    result = self.airtable_service.create_task(
                        params["task_name"], 
                        params["description"], 
                        params["deadline"], 
                        params["status"]
                    )
                    
                    # Se chegou aqui, a tarefa foi criada com sucesso
                    response = f"✅ Tarefa '{params['task_name']}' criada com sucesso!"
                
                except ConfigurationError as e:
                    response = f"🔴 Erro de configuração: {str(e)}"
                
                except AirtableApiError as e:
                    response = f"🔴 Erro na API do Airtable: {str(e)}"
                
                except Exception as e:
                    # Captura qualquer outra exceção não esperada
                    response = f"🔴 Erro inesperado: {str(e)}"
                    raise CommandProcessingError(f"Erro ao criar tarefa: {str(e)}", command)
                
                # Substitui o comando pelo resultado no texto
                # Isso permite que o usuário veja o resultado da operação
                processed_text = processed_text.replace(command, response)
        
        return processed_text
    
    def process_list_tasks_command(self, text):
        """
        Processa comandos de listagem de tarefas no texto
        
        Args:
            text (str): Texto que pode conter comandos de listagem de tarefas
            
        Returns:
            str: Texto processado com os resultados dos comandos
            
        Raises:
            CommandProcessingError: Se ocorrer um erro no processamento dos comandos
        """
        processed_text = text
        
        if "[[AIRTABLE_LIST_TASKS]]" in processed_text:
            try:
                # Obtém as tarefas
                result = self.airtable_service.list_tasks()
                
                # Prepara a resposta
                tasks = result.get("records", [])
                if not tasks:
                    response = "📋 Nenhuma tarefa encontrada."
                else:
                    response = "📋 Tarefas encontradas:\n\n"
                    for i, task in enumerate(tasks, 1):
                        fields = task.get("fields", {})
                        response += f"{i}. {fields.get('Task', 'Sem nome')}\n"
                        if "Status" in fields:
                            response += f"   Status: {fields['Status']}\n"
                        if "Notes" in fields:
                            response += f"   Descrição: {fields['Notes']}\n"
                        if "Deadline" in fields:
                            response += f"   Data limite: {fields['Deadline']}\n"
                        response += "\n"
            
            except ConfigurationError as e:
                response = f"🔴 Erro de configuração: {str(e)}"
            
            except AirtableApiError as e:
                response = f"🔴 Erro na API do Airtable: {str(e)}"
            
            except Exception as e:
                # Captura qualquer outra exceção não esperada
                response = f"🔴 Erro inesperado: {str(e)}"
                raise CommandProcessingError(f"Erro ao listar tarefas: {str(e)}", "[[AIRTABLE_LIST_TASKS]]")
            
            # Substitui o comando pelo resultado
            processed_text = processed_text.replace("[[AIRTABLE_LIST_TASKS]]", response)
        
        return processed_text 