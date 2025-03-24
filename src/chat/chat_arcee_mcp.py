#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chat Interativo com Arcee + MCP (Refatorado)

Implementação refatorada do chat interativo utilizando
interfaces e adaptadores.
"""

import os
import sys
import re
import json
import requests
from typing import Dict, List, Any, Optional, Union

from src.interfaces.llm_client import LLMClient
from src.interfaces.task_service import TaskService
from src.interfaces.mcp_service import MCPService
from src.factories.service_factory import ServiceFactory
from src.chat.command_processor import CommandProcessor
from src.chat.chat_history import ChatHistory
from src.chat.chat_ui import ChatUI
from src.exceptions import ConfigurationError, LLMApiError, CommandProcessingError, AirtableApiError

class ChatArceeMCP:
    """Implementação de chat interativo com Arcee e MCP (refatorada)"""
    
    def __init__(self):
        """
        Inicializa o chat Arcee + MCP
        
        Cria as instâncias de serviços, configura o histórico
        e prepara a interface.
        """
        # Inicializa o cliente LLM
        self.client = ServiceFactory.create_llm_client()
        
        # Inicializa o serviço MCP
        self.mcp_service = ServiceFactory.create_mcp_service()
        
        # Inicializa o serviço de tarefas
        self.task_service = ServiceFactory.create_task_service()
        
        # Inicializa o processador de comandos
        self.command_processor = CommandProcessor(self.task_service)
        
        # Inicializa o histórico de chat
        self.history = ChatHistory()
        
        # Inicializa a interface de usuário
        self.ui = ChatUI()
        
        # Adiciona context de sistema ao iniciar
        self._add_system_context()
    
    def _add_system_context(self):
        """Adiciona contexto de sistema ao histórico"""
        # Obtém os nomes dos servidores MCP disponíveis
        mcp_servers = self.mcp_service.list_available_servers()
        
        # Cria uma mensagem de contexto informando sobre os servidores disponíveis
        context = (
            "Você é o Arcee, um assistente IA especializado em Python e desenvolvimento de software. "
            "Você tem acesso a servidores MCP (Multi-agent Cognitive Protocol) que oferecem "
            "ferramentas adicionais para realizar tarefas. "
            f"Servidores MCP disponíveis: {', '.join(mcp_servers)}.\n\n"
            "Comandos especiais:\n"
            "- [[AIRTABLE_CREATE_TASK: Nome da Tarefa | Descrição | Data Limite | Status]] - Cria uma tarefa no Airtable\n"
            "- [[AIRTABLE_LIST_TASKS]] - Lista as tarefas existentes no Airtable\n"
            "- [[AIRTABLE_DELETE_TASK: ID_DA_TAREFA]] - Exclui uma tarefa com o ID especificado\n"
            "- [[AIRTABLE_BULK_DELETE_TASKS: ID1,ID2,ID3]] - Exclui múltiplas tarefas de uma vez\n\n"
            "Você pode usar linguagem natural para comandos, por exemplo:\n"
            "- 'excluir tarefa com id rec123456' - Exclui a tarefa com ID rec123456\n"
            "- 'apagar tarefas com ids rec123,rec456' - Exclui múltiplas tarefas\n"
        )
        
        # Adiciona ao histórico
        self.history.add_message("system", context)
    
    def run(self):
        """
        Executa o loop principal do chat interativo
        
        Returns:
            int: Código de saída (0 = sucesso, outros = erro)
        """
        # Verifica se o cliente LLM foi inicializado
        if not self.client.is_initialized():
            print("❌ Cliente LLM não inicializado.")
            return 1
        
        # Exibe mensagem de boas-vindas
        model_info = self.client.get_model_info()
        mode = model_info.get("mode", "desconhecido") if model_info else "desconhecido"
        
        self.ui.show_welcome_message(self.mcp_service.list_available_servers())
        
        # Loop principal
        while True:
            # Obtém entrada do usuário
            user_input = self.ui.get_user_input()
            
            # Verifica comandos especiais de interface
            if user_input.lower() in ["sair", "exit", "quit"]:
                self.ui.show_goodbye()
                return 0
            
            if user_input.lower() in ["limpar", "clear"]:
                self.history.clear()
                self._add_system_context()
                self.ui.show_history_cleared()
                continue
            
            # Envia mensagem e obtém resposta
            self.ui.show_thinking()
            
            try:
                response = self.send_message(user_input)
                
                # Exibe resposta processada se disponível, ou a resposta original
                text = response.get("processed_text", response.get("text", "Sem resposta"))
                self.ui.show_response(text)
                
                # Exibe informações do modelo se disponíveis
                self.ui.show_model_info(response)
            
            except LLMApiError as e:
                self.ui.show_error(f"Erro na API do modelo: {e}")
            
            except CommandProcessingError as e:
                self.ui.show_error(f"Erro ao processar comandos: {e}")
            
            except ConfigurationError as e:
                self.ui.show_error(f"Erro de configuração: {e}")
            
            except AirtableApiError as e:
                self.ui.show_error(f"Erro na API do Airtable: {e}")
            
            except Exception as e:
                self.ui.show_error(f"Erro: {e}")
                # Log detalhado para erros inesperados
                import traceback
                traceback.print_exc()
    
    def add_to_history(self, role, message):
        """
        Adiciona uma mensagem ao histórico
        
        Args:
            role (str): Papel do emissor ("user", "assistant" ou "system")
            message (str): Conteúdo da mensagem
        """
        self.history.add_message(role, message)
    
    def send_message(self, message: str):
        """
        Envia uma mensagem para o modelo e retorna a resposta
        
        Args:
            message (str): Mensagem do usuário
            
        Returns:
            dict: Resposta do modelo ou None se ocorrer erro
            
        Raises:
            LLMApiError: Se ocorrer um erro na comunicação com a API do modelo
            CommandProcessingError: Se ocorrer um erro no processamento dos comandos
        """
        # Adiciona a mensagem do usuário ao histórico
        self.add_to_history("user", message)
        
        try:
            # Cria uma cópia do histórico para enviar ao modelo
            # Usamos uma cópia para evitar mutações não intencionais
            messages = self.history.get_messages()
            
            # Envia a mensagem para o modelo Arcee
            response = self.client.send_message(messages)
            
            # Verifica se houve erro na API
            if "error" in response and response["error"]:
                raise LLMApiError(response["error"], response)
            
            # Processa comandos especiais embutidos na resposta
            try:
                processed_text = self.command_processor.process_commands(response["text"])
                
                # Detecta a presença de comandos não tradicionais relacionados a tarefas
                task_commands = self._detect_task_commands(processed_text)
                if task_commands:
                    self.ui.print_status(f"Detectados {len(task_commands)} comandos relacionados a tarefas")
                    processed_text = self._process_task_commands(processed_text, task_commands)
            except CommandProcessingError as e:
                print(f"\n⚠️ Aviso: Erro ao processar comandos: {e}")
                processed_text = response["text"]
            
            # Atualiza o texto processado na resposta
            # Mas mantém o texto original para o histórico
            response["processed_text"] = processed_text
            
            # Adiciona a resposta ao histórico
            # Importante: Usamos o texto original (não processado) para que
            # comandos não sejam executados novamente em conversas futuras
            self.add_to_history("assistant", response["text"])
            
            # Retorna a resposta completa incluindo metadados
            return response
        
        except LLMApiError as e:
            raise e
        except ConfigurationError as e:
            raise e
        except AirtableApiError as e:
            raise e
        except CommandProcessingError as e:
            raise e
        except requests.exceptions.RequestException as e:
            raise LLMApiError(f"Erro de comunicação com API: {str(e)}")
        except Exception as e:
            # Captura qualquer outra exceção não esperada
            import traceback
            print(f"\n❌ Erro inesperado: {e}")
            traceback.print_exc()
            raise e
    
    def _detect_task_commands(self, text: str) -> List[Dict[str, Any]]:
        """
        Detecta comandos relacionados a tarefas em linguagem natural
        
        Args:
            text (str): Texto a ser analisado
            
        Returns:
            List[Dict[str, Any]]: Lista de comandos detectados
        """
        commands = []
        
        # Padrões para detectar comandos relacionados a tarefas
        patterns = {
            "delete": [
                r"(?i)excluir\s+tarefa\s+(?:com\s+)?id\s*[:]?\s*(\w+)",
                r"(?i)apagar\s+tarefa\s+(?:com\s+)?id\s*[:]?\s*(\w+)",
                r"(?i)deletar\s+tarefa\s+(?:com\s+)?id\s*[:]?\s*(\w+)",
            ],
            "bulk_delete": [
                r"(?i)excluir\s+tarefas\s+(?:com\s+)?ids\s*[:]?\s*([\w,\s]+)",
                r"(?i)apagar\s+tarefas\s+(?:com\s+)?ids\s*[:]?\s*([\w,\s]+)",
                r"(?i)deletar\s+tarefas\s+(?:com\s+)?ids\s*[:]?\s*([\w,\s]+)",
            ]
        }
        
        # Busca por padrões de exclusão individual
        for pattern in patterns["delete"]:
            matches = re.finditer(pattern, text)
            for match in matches:
                task_id = match.group(1).strip()
                if task_id and task_id.lower() not in ["id_da_tarefa", "task_id"]:
                    commands.append({
                        "type": "delete",
                        "task_id": task_id,
                        "match": match.group(0)
                    })
        
        # Busca por padrões de exclusão em massa
        for pattern in patterns["bulk_delete"]:
            matches = re.finditer(pattern, text)
            for match in matches:
                ids_text = match.group(1).strip()
                task_ids = [id.strip() for id in ids_text.split(',')]
                valid_ids = [id for id in task_ids if id and id.lower() not in ["id_da_tarefa", "id1", "id2", "id3"]]
                if valid_ids:
                    commands.append({
                        "type": "bulk_delete",
                        "task_ids": valid_ids,
                        "match": match.group(0)
                    })
        
        return commands
    
    def _process_task_commands(self, text: str, commands: List[Dict[str, Any]]) -> str:
        """
        Processa comandos de tarefas detectados
        
        Args:
            text (str): Texto original
            commands (List[Dict[str, Any]]): Lista de comandos a processar
            
        Returns:
            str: Texto com resultados dos comandos
        """
        processed_text = text
        
        for cmd in commands:
            try:
                if cmd["type"] == "delete":
                    task_id = cmd["task_id"]
                    self.ui.show_thinking()
                    result = self.task_service.delete_task(task_id)
                    replacement = f"✅ Tarefa com ID '{task_id}' excluída com sucesso!"
                
                elif cmd["type"] == "bulk_delete":
                    task_ids = cmd["task_ids"]
                    self.ui.show_thinking()
                    
                    success_count = 0
                    error_count = 0
                    details = []
                    
                    for task_id in task_ids:
                        try:
                            self.task_service.delete_task(task_id)
                            details.append(f"✅ Tarefa {task_id}: Excluída com sucesso")
                            success_count += 1
                        except Exception as e:
                            details.append(f"❌ Tarefa {task_id}: Erro - {str(e)}")
                            error_count += 1
                    
                    replacement = f"🔄 Resultado da exclusão em massa:\n\n"
                    replacement += "\n".join(details)
                    replacement += f"\n\nResumo: {success_count} tarefas excluídas com sucesso, {error_count} erros."
                
                # Substitui o comando pelo resultado
                processed_text = processed_text.replace(cmd["match"], replacement)
            
            except Exception as e:
                error_msg = f"🔴 Erro ao processar comando: {str(e)}"
                processed_text = processed_text.replace(cmd["match"], error_msg)
        
        return processed_text 