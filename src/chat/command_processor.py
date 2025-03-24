#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Processador de comandos para o chat

Este módulo define o processador de comandos especiais para o 
chat, permitindo executar ações específicas a partir do texto.
"""

import re
import json
import os
from typing import Dict, List, Any, Tuple, Optional, Union
from datetime import datetime

# Importa as exceções personalizadas
from src.exceptions import CommandProcessingError


class CommandProcessor:
    """
    Processador de comandos especiais em texto de chat.
    
    Esta classe identifica e processa comandos especiais no formato
    "/comando argumentos" em texto de chat.
    
    Attributes:
        task_service: Serviço para gerenciamento de tarefas.
        mcp_service: Serviço para interação com MCP.
        veyrax_service: Serviço para interação com Veyrax.
    """
    
    def __init__(self, task_service=None, mcp_service=None, veyrax_service=None):
        """
        Inicializa o processador de comandos.
        
        Args:
            task_service: Serviço para gerenciamento de tarefas (opcional).
            mcp_service: Serviço para interação com MCP (opcional).
            veyrax_service: Serviço para interação com Veyrax (opcional).
        """
        self.task_service = task_service
        self.mcp_service = mcp_service
        self.veyrax_service = veyrax_service
        self.base_id = os.environ.get("AIRTABLE_BASE_ID", "appt2CRa7k9cUASRJ")
        self.table_name = os.environ.get("AIRTABLE_TABLE_ID", "tblUatmXxgQnqEUDB")
        
        # Expressão regular para identificar comandos
        self.command_pattern = re.compile(r'^/(\w+)\s*(.*?)$', re.MULTILINE)
        
        # Padrões para comandos em linguagem natural
        self.natural_command_patterns = [
            # Padrões para buscar tarefas
            (r'(?i)(?:mostrar?|exibir?|listar?|buscar?)\s+(?:as\s+)?tarefas\s+(?:com\s+)?(?:status\s+)?(?:conclu[ií]d[ao]s?|(?:em\s+)?done)', 
             self._process_natural_list_done_tasks),
            
            # Padrões para excluir tarefas concluídas
            (r'(?i)(?:excluir?|apagar?|deletar?|remover?)\s+(?:as\s+)?tarefas\s+(?:com\s+)?(?:status\s+)?(?:conclu[ií]d[ao]s?|(?:em\s+)?done)', 
             self._process_natural_delete_done_tasks),
            
            # Padrões para contar tarefas
            (r'(?i)(?:quant[ao]s?|contar?)\s+tarefas\s+(?:com\s+)?(?:status\s+)?(\w+)',
             self._process_natural_count_tasks),
             
            # Padrões para tarefas recentes
            (r'(?i)(?:mostrar?|exibir?|listar?|buscar?)\s+(?:as\s+)?(?:tarefas\s+)?(?:recentes|últimas|novas)',
             self._process_natural_recent_tasks)
        ]
    
    def process_text(self, text: str) -> Tuple[bool, str]:
        """
        Processa o texto para identificar e executar comandos.
        
        Args:
            text: Texto a ser processado.
            
        Returns:
            Tupla contendo (sucesso, resposta).
        """
        # Verifica se há algum comando no texto
        match = self.command_pattern.search(text)
        if match:
            command = match.group(1).lower()
            args = match.group(2).strip()
            
            # Comando de ajuda
            if command == 'help':
                return True, self._get_help_text()
                
            # Comandos de tarefas
            elif command == 'task' or command == 'tarefa':
                if self.task_service:
                    return self._process_task_command(args)
                else:
                    return True, "Serviço de tarefas não disponível."
                    
            # Comandos MCP
            elif command == 'mcp':
                if self.mcp_service:
                    return self._process_mcp_command(args)
                else:
                    return True, "Serviço MCP não disponível."
                    
            # Comandos Veyrax
            elif command == 'veyrax':
                if self.veyrax_service:
                    return self._process_veyrax_command(args)
                else:
                    return True, "Serviço Veyrax não disponível."
            
            # Comando não reconhecido
            return True, f"Comando '{command}' não reconhecido. Digite /help para ver os comandos disponíveis."
        
        # Verifica se há um comando em linguagem natural
        for pattern, handler in self.natural_command_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return True, handler()
                except Exception as e:
                    return True, f"Erro ao processar comando em linguagem natural: {str(e)}"
        
        # Se não for um comando, retorna o texto original
        return False, text
    
    def _process_task_command(self, args: str) -> Tuple[bool, str]:
        """
        Processa um comando de tarefa.
        
        Args:
            args: Argumentos do comando.
            
        Returns:
            Tupla contendo (sucesso, resposta).
        """
        # Divide os argumentos em partes
        parts = args.split(maxsplit=1)
        if not parts:
            return True, "Comando de tarefa inválido. Use /task list, /task add <descrição>, etc."
            
        sub_command = parts[0].lower()
        
        # Comando para listar tarefas
        if sub_command == 'list' or sub_command == 'listar':
            try:
                tasks = self.task_service.list_tasks()
                if not tasks:
                    return True, "Não há tarefas registradas."
                
                response = "📋 Lista de tarefas:\n\n"
                for i, task in enumerate(tasks, 1):
                    status = "✅" if task.get('completed') else "⬜"
                    response += f"{i}. {status} {task.get('description')}\n"
                
                return True, response
            except Exception as e:
                return True, f"Erro ao listar tarefas: {str(e)}"
        
        # Comando para adicionar uma tarefa
        elif sub_command == 'add' or sub_command == 'adicionar':
            if len(parts) < 2:
                return True, "Descrição da tarefa não fornecida. Use /task add <descrição>"
            
            description = parts[1]
            try:
                task = self.task_service.add_task(description)
                return True, f"✅ Tarefa adicionada: {description}"
            except Exception as e:
                return True, f"Erro ao adicionar tarefa: {str(e)}"
        
        # Comando para concluir uma tarefa
        elif sub_command == 'complete' or sub_command == 'concluir':
            if len(parts) < 2:
                return True, "ID da tarefa não fornecido. Use /task complete <id>"
            
            try:
                task_id = parts[1]
                self.task_service.complete_task(task_id)
                return True, f"✅ Tarefa {task_id} marcada como concluída."
            except Exception as e:
                return True, f"Erro ao concluir tarefa: {str(e)}"
        
        # Comando para excluir uma tarefa
        elif sub_command == 'delete' or sub_command == 'excluir':
            if len(parts) < 2:
                return True, "ID da tarefa não fornecido. Use /task delete <id>"
            
            try:
                task_id = parts[1]
                self.task_service.delete_task(task_id)
                return True, f"🗑️ Tarefa {task_id} excluída."
            except Exception as e:
                return True, f"Erro ao excluir tarefa: {str(e)}"
        
        # Subcomando não reconhecido
        return True, f"Subcomando de tarefa '{sub_command}' não reconhecido. Use /help para ver os comandos disponíveis."
    
    def _process_mcp_command(self, args: str) -> Tuple[bool, str]:
        """
        Processa um comando MCP.
        
        Args:
            args: Argumentos do comando.
            
        Returns:
            Tupla contendo (sucesso, resposta).
        """
        # Divide os argumentos em partes
        parts = args.split(maxsplit=1)
        if not parts:
            return True, "Comando MCP inválido. Use /mcp tools, /mcp run <ferramenta> <método>, etc."
            
        sub_command = parts[0].lower()
        
        # Comando para listar ferramentas MCP
        if sub_command == 'tools' or sub_command == 'ferramentas':
            try:
                tools = self.mcp_service.get_tools()
                response = "🛠️ Ferramentas MCP disponíveis:\n\n"
                for tool_name, tool_info in tools.items():
                    response += f"- {tool_name}: {tool_info.get('description', 'Sem descrição')}\n"
                    if 'methods' in tool_info:
                        response += f"  Métodos: {', '.join(tool_info['methods'])}\n"
                
                return True, response
            except Exception as e:
                print(f"Erro ao listar ferramentas MCP: {str(e)}")
                return True, f"❌ Erro ao listar ferramentas MCP: {str(e)}"
        
        # Comando para executar uma ferramenta MCP
        elif sub_command == 'run' or sub_command == 'executar':
            if len(parts) < 2:
                return True, "Argumentos insuficientes. Use /mcp run <ferramenta> <método> [parâmetros JSON]"
            
            run_args = parts[1].split(maxsplit=2)
            if len(run_args) < 2:
                return True, "Ferramenta ou método não informados. Use /mcp run <ferramenta> <método> [parâmetros JSON]"
            
            tool = run_args[0]
            method = run_args[1]
            parameters = {}
            
            # Se houver parâmetros JSON, tenta fazer parse
            if len(run_args) >= 3:
                try:
                    parameters = json.loads(run_args[2])
                except json.JSONDecodeError:
                    return True, "Erro nos parâmetros JSON. Verifique a sintaxe."
            
            try:
                result = self.mcp_service.tool_call(
                    tool_name=tool,
                    method_name=method,
                    parameters=parameters
                )
                response = f"✅ Resultado da execução de {tool}.{method}:\n\n"
                response += json.dumps(result, indent=2, ensure_ascii=False)
                return True, response
            except Exception as e:
                print(f"Erro ao executar ferramenta MCP: {str(e)}")
                return True, f"❌ Erro ao executar ferramenta MCP: {str(e)}"
        
        # Subcomando não reconhecido
        return True, f"Subcomando MCP '{sub_command}' não reconhecido. Use /help para ver os comandos disponíveis."
    
    def _process_veyrax_command(self, args: str) -> Tuple[bool, str]:
        """
        Processa um comando Veyrax.
        
        Args:
            args: Argumentos do comando.
            
        Returns:
            Tupla contendo (sucesso, resposta).
        """
        # Divide os argumentos em partes
        parts = args.split(maxsplit=1)
        if not parts:
            return True, "Comando Veyrax inválido. Use /veyrax tools, /veyrax run <ferramenta> <método>, etc."
            
        sub_command = parts[0].lower()
        
        # Comando para listar ferramentas Veyrax
        if sub_command == 'tools' or sub_command == 'ferramentas':
            try:
                tools = self.veyrax_service.get_tools()
                response = "🛠️ Ferramentas Veyrax disponíveis:\n\n"
                for tool in tools:
                    response += f"- {tool['name']}: {tool.get('description', 'Sem descrição')}\n"
                    if 'methods' in tool:
                        methods = [m['name'] for m in tool.get('methods', [])]
                        response += f"  Métodos: {', '.join(methods)}\n"
                
                return True, response
            except Exception as e:
                print(f"Erro ao listar ferramentas Veyrax: {str(e)}")
                return True, f"❌ Erro ao listar ferramentas Veyrax: {str(e)}"
        
        # Comando para executar uma ferramenta Veyrax
        elif sub_command == 'run' or sub_command == 'executar':
            if len(parts) < 2:
                return True, "Argumentos insuficientes. Use /veyrax run <ferramenta> <método> [parâmetros JSON]"
            
            run_args = parts[1].split(maxsplit=2)
            if len(run_args) < 2:
                return True, "Ferramenta ou método não informados. Use /veyrax run <ferramenta> <método> [parâmetros JSON]"
            
            tool = run_args[0]
            method = run_args[1]
            parameters = {}
            
            # Se houver parâmetros JSON, tenta fazer parse
            if len(run_args) >= 3:
                try:
                    parameters = json.loads(run_args[2])
                except json.JSONDecodeError:
                    return True, "Erro nos parâmetros JSON. Verifique a sintaxe."
            
            try:
                result = self.veyrax_service.execute_tool(
                    tool_name=tool,
                    method_name=method,
                    parameters=parameters
                )
                response = f"✅ Resultado da execução de {tool}.{method}:\n\n"
                response += json.dumps(result, indent=2, ensure_ascii=False)
                return True, response
            except Exception as e:
                print(f"Erro ao executar ferramenta Veyrax: {str(e)}")
                return True, f"❌ Erro ao executar ferramenta Veyrax: {str(e)}"
        
        # Comandos para gerenciamento de memórias
        elif sub_command == 'memory' or sub_command == 'memória':
            if len(parts) < 2:
                return True, "Argumentos insuficientes. Use /veyrax memory save/list/delete [parâmetros]"
            
            memory_args = parts[1].split(maxsplit=1)
            memory_cmd = memory_args[0].lower()
            
            # Salvar memória
            if memory_cmd == 'save' or memory_cmd == 'salvar':
                if len(memory_args) < 2:
                    return True, "Texto da memória não fornecido. Use /veyrax memory save <texto>"
                
                try:
                    memory_text = memory_args[1]
                    result = self.veyrax_service.execute_tool(
                        tool_name="memory",
                        method_name="save_memory",
                        parameters={
                            "text": memory_text
                        }
                    )
                    return True, f"✅ Memória salva com sucesso. ID: {result.get('id', 'N/A')}"
                except Exception as e:
                    print(f"Erro ao salvar memória: {str(e)}")
                    return True, f"❌ Erro ao salvar memória: {str(e)}"
            
            # Listar memórias
            elif memory_cmd == 'list' or memory_cmd == 'listar':
                try:
                    result = self.veyrax_service.execute_tool(
                        tool_name="memory",
                        method_name="get_memories",
                        parameters={
                            "limit": 10
                        }
                    )
                    
                    memories = result.get("memories", [])
                    if not memories:
                        return True, "Não há memórias armazenadas."
                    
                    response = f"📋 Memórias ({len(memories)} encontradas):\n\n"
                    for memory in memories:
                        response += f"- ID: {memory.get('id')}\n"
                        response += f"  Data: {memory.get('created_at', 'N/A')}\n"
                        response += f"  Conteúdo: {memory.get('text')}\n\n"
                    
                    return True, response
                except Exception as e:
                    print(f"Erro ao listar memórias: {str(e)}")
                    return True, f"❌ Erro ao listar memórias: {str(e)}"
            
            # Excluir memória
            elif memory_cmd == 'delete' or memory_cmd == 'excluir':
                if len(memory_args) < 2:
                    return True, "ID da memória não fornecido. Use /veyrax memory delete <id>"
                
                try:
                    memory_id = memory_args[1]
                    result = self.veyrax_service.execute_tool(
                        tool_name="memory",
                        method_name="delete_memory",
                        parameters={
                            "memory_id": memory_id
                        }
                    )
                    
                    if result.get("success"):
                        return True, f"🗑️ Memória {memory_id} excluída com sucesso."
                    else:
                        return True, f"❌ Erro ao excluir memória: {result.get('error', 'Erro desconhecido')}"
                except Exception as e:
                    print(f"Erro ao excluir memória: {str(e)}")
                    return True, f"❌ Erro ao excluir memória: {str(e)}"
            
            else:
                return True, f"Subcomando de memória '{memory_cmd}' não reconhecido. Use save, list ou delete."
        
        # Comandos para envio de e-mail
        elif sub_command == 'email':
            if len(parts) < 2:
                return True, "Argumentos insuficientes. Use /veyrax email send <destinatário> <assunto> <corpo>"
            
            email_args = parts[1].split(maxsplit=1)
            email_cmd = email_args[0].lower()
            
            # Enviar e-mail
            if email_cmd == 'send' or email_cmd == 'enviar':
                if len(email_args) < 2:
                    return True, "Parâmetros insuficientes. Use /veyrax email send <destinatário> <assunto> <corpo>"
                
                try:
                    # Tenta extrair os parâmetros
                    email_params = email_args[1].split(maxsplit=2)
                    
                    if len(email_params) < 3:
                        return True, "Parâmetros insuficientes. Use /veyrax email send <destinatário> <assunto> <corpo>"
                    
                    to = email_params[0]
                    subject = email_params[1]
                    body = email_params[2]
                    
                    result = self.veyrax_service.execute_tool(
                        tool_name="email",
                        method_name="send_email",
                        parameters={
                            "to": to,
                            "subject": subject,
                            "body": body
                        }
                    )
                    
                    return True, f"✅ E-mail enviado com sucesso para {to}. ID da mensagem: {result.get('message_id', 'N/A')}"
                except Exception as e:
                    print(f"Erro ao enviar e-mail: {str(e)}")
                    return True, f"❌ Erro ao enviar e-mail: {str(e)}"
            
            else:
                return True, f"Subcomando de e-mail '{email_cmd}' não reconhecido. Use send."
        
        # Subcomando não reconhecido
        return True, f"Subcomando Veyrax '{sub_command}' não reconhecido. Use /help para ver os comandos disponíveis."
    
    def _process_natural_list_done_tasks(self):
        """
        Processa o comando de listagem de tarefas concluídas.
        
        Returns:
            Mensagem com a lista de tarefas concluídas.
        """
        try:
            # Busca tarefas no Airtable
            result = self.veyrax_service.execute_tool(
                tool_name="airtable",
                method_name="list_records",
                parameters={
                    "base_id": self.base_id,
                    "table_name": self.table_name
                }
            )
            
            if not result.get("success"):
                return f"❌ Não foi possível listar as tarefas. Erro: {result.get('error', 'Erro desconhecido')}"
            
            # Filtra apenas as tarefas concluídas
            records = result.get("records", [])
            done_tasks = [r for r in records if r.get("fields", {}).get("Status") == "Done"]
            
            if not done_tasks:
                return "📋 Não há tarefas concluídas."
            
            # Formata a resposta
            response = "📋 Tarefas concluídas:\n\n"
            for i, task in enumerate(done_tasks, 1):
                task_id = task.get("id", "")
                task_name = task.get("fields", {}).get("Name", "Sem nome")
                completed_date = task.get("fields", {}).get("Completed", "Data não informada")
                response += f"{i}. {task_name} (ID: {task_id}, concluída em: {completed_date})\n"
                
            return response
            
        except Exception as e:
            print(f"Erro ao listar tarefas concluídas: {str(e)}")
            return f"❌ Erro ao listar tarefas concluídas: {str(e)}"
    
    def _process_natural_delete_done_tasks(self):
        """
        Processa o comando de exclusão de tarefas concluídas.
        
        Returns:
            Mensagem confirmando a exclusão ou indicando erro.
        """
        try:
            # Busca tarefas no Airtable
            result = self.veyrax_service.execute_tool(
                tool_name="airtable",
                method_name="list_records",
                parameters={
                    "base_id": self.base_id,
                    "table_name": self.table_name
                }
            )
            
            if not result.get("success"):
                return f"❌ Não foi possível listar as tarefas. Erro: {result.get('error', 'Erro desconhecido')}"
            
            # Filtra apenas as tarefas concluídas
            records = result.get("records", [])
            done_tasks = [r for r in records if r.get("fields", {}).get("Status") == "Done"]
            
            if not done_tasks:
                return "📋 Não há tarefas concluídas para excluir."
            
            # Exclui cada tarefa concluída
            deleted_count = 0
            for task in done_tasks:
                delete_result = self.veyrax_service.execute_tool(
                    tool_name="airtable",
                    method_name="delete_record",
                    parameters={
                        "base_id": self.base_id,
                        "table_name": self.table_name,
                        "record_id": task.get("id")
                    }
                )
                
                if delete_result.get("success"):
                    deleted_count += 1
            
            if deleted_count == 0:
                return "❌ Não foi possível excluir nenhuma tarefa concluída."
            elif deleted_count < len(done_tasks):
                return f"⚠️ Algumas tarefas concluídas foram excluídas ({deleted_count} de {len(done_tasks)})."
            else:
                return f"✅ Todas as tarefas concluídas foram excluídas com sucesso ({deleted_count} tarefas)."
                
        except Exception as e:
            print(f"Erro ao excluir tarefas concluídas: {str(e)}")
            return f"❌ Erro ao excluir tarefas concluídas: {str(e)}"
    
    def _process_natural_count_tasks(self):
        """
        Processa o comando para contar tarefas por status.
        
        Returns:
            Mensagem com o contador de tarefas por status.
        """
        try:
            # Busca tarefas no Airtable
            result = self.veyrax_service.execute_tool(
                tool_name="airtable",
                method_name="list_records",
                parameters={
                    "base_id": self.base_id,
                    "table_name": self.table_name
                }
            )
            
            if not result.get("success"):
                return f"❌ Não foi possível contar as tarefas. Erro: {result.get('error', 'Erro desconhecido')}"
            
            # Conta tarefas por status
            records = result.get("records", [])
            status_counts = {}
            
            for record in records:
                status = record.get("fields", {}).get("Status", "Sem status")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Formata a resposta
            if not status_counts:
                return "📋 Não há tarefas para contar."
                
            response = "📊 Contagem de tarefas por status:\n\n"
            for status, count in status_counts.items():
                response += f"{status}: {count} tarefa(s)\n"
                
            response += f"\nTotal: {len(records)} tarefa(s)"
            return response
            
        except Exception as e:
            print(f"Erro ao contar tarefas: {str(e)}")
            return f"❌ Erro ao contar tarefas: {str(e)}"
    
    def _process_natural_recent_tasks(self):
        """
        Processa o comando para listar tarefas recentes.
        
        Returns:
            Mensagem com a lista de tarefas mais recentes.
        """
        try:
            # Busca tarefas no Airtable
            result = self.veyrax_service.execute_tool(
                tool_name="airtable",
                method_name="list_records",
                parameters={
                    "base_id": self.base_id,
                    "table_name": self.table_name
                }
            )
            
            if not result.get("success"):
                return f"❌ Não foi possível listar as tarefas recentes. Erro: {result.get('error', 'Erro desconhecido')}"
            
            # Organiza por data (mais recentes primeiro)
            records = result.get("records", [])
            
            # Tentativa de ordenar por data, se disponível
            try:
                records.sort(key=lambda x: x.get("fields", {}).get("Created", ""), reverse=True)
            except:
                pass  # Ignora erros de ordenação
                
            # Pega as 5 mais recentes
            recent_tasks = records[:5]
            
            if not recent_tasks:
                return "📋 Não há tarefas recentes."
                
            # Formata a resposta
            response = "📋 Tarefas mais recentes:\n\n"
            for i, task in enumerate(recent_tasks, 1):
                task_id = task.get("id", "")
                task_name = task.get("fields", {}).get("Name", "Sem nome")
                status = task.get("fields", {}).get("Status", "Sem status")
                created_date = task.get("fields", {}).get("Created", "Data não informada")
                response += f"{i}. {task_name} (ID: {task_id}, {status}) - {created_date}\n"
                
            return response
                
        except Exception as e:
            print(f"Erro ao listar tarefas recentes: {str(e)}")
            return f"❌ Erro ao listar tarefas recentes: {str(e)}"
    
    def _get_help_text(self) -> str:
        """
        Retorna o texto de ajuda com os comandos disponíveis.
        
        Returns:
            Texto de ajuda.
        """
        help_text = "📋 Comandos disponíveis:\n\n"
        
        # Comandos básicos
        help_text += "Comandos básicos:\n"
        help_text += "  /help - Exibe esta ajuda\n"
        help_text += "  /task <descrição> - Adiciona uma nova tarefa\n"
        help_text += "  /done <id> - Marca uma tarefa como concluída\n"
        help_text += "  /list - Lista todas as tarefas pendentes\n"
        help_text += "  /delete <id> - Exclui uma tarefa\n\n"
        
        # Comandos adicionais
        help_text += "Comandos adicionais:\n"
        help_text += "  /listdone - Lista tarefas concluídas\n"
        help_text += "  /deletedone - Remove todas as tarefas concluídas\n"
        help_text += "  /count - Conta tarefas por status\n"
        help_text += "  /recent - Lista as tarefas mais recentes\n\n"
        
        # Linguagem natural
        help_text += "Comandos em linguagem natural:\n"
        help_text += "  \"mostrar tarefas concluídas\" - Lista tarefas com status 'Done'\n"
        help_text += "  \"excluir tarefas concluídas\" - Remove todas as tarefas com status 'Done'\n"
        help_text += "  \"quantas tarefas pendentes\" - Conta tarefas com um status específico\n"
        help_text += "  \"mostrar tarefas recentes\" - Lista as tarefas mais recentes\n\n"
        
        help_text += "Você pode usar tanto comandos específicos quanto linguagem natural para interagir com o sistema."
        
        return help_text

    def _process_specific_command(self, command: str) -> Tuple[bool, str]:
        """
        Processa comandos específicos no formato /comando.
        
        Args:
            command: Texto do comando.
            
        Returns:
            Tupla contendo (sucesso, resposta).
        """
        match = self.command_pattern.match(command)
        if not match:
            return False, "Formato de comando inválido."
            
        cmd = match.group(1)
        args = match.group(2).strip() if match.group(2) else ""
        
        if cmd == "help":
            return True, self._get_help_text()
            
        elif cmd == "task":
            if not args:
                return False, "Você precisa especificar uma tarefa."
            return self._add_task(args)
            
        elif cmd == "done":
            if not args:
                return False, "Você precisa especificar o ID da tarefa."
            return self._complete_task(args)
            
        elif cmd == "list":
            return self._list_tasks()
            
        elif cmd == "delete":
            if not args:
                return False, "Você precisa especificar o ID da tarefa."
            return self._delete_task(args)
        
        # Comandos adicionais
        elif cmd == "listdone":
            return True, self._process_natural_list_done_tasks()
            
        elif cmd == "deletedone":
            return True, self._process_natural_delete_done_tasks()
            
        elif cmd == "count":
            return True, self._process_natural_count_tasks()
            
        elif cmd == "recent":
            return True, self._process_natural_recent_tasks()
        
        return False, f"Comando '/{cmd}' não reconhecido. Use /help para ver os comandos disponíveis."

    def process_command(self, user_input: str) -> Tuple[bool, str]:
        """
        Processa um comando do usuário.
        
        Args:
            user_input: Texto de entrada do usuário.
            
        Returns:
            Tupla contendo (sucesso, resposta).
        """
        # Verifica se é um comando específico
        if self.command_pattern.match(user_input):
            return self._process_specific_command(user_input)
        
        # Tenta processar como linguagem natural
        if "tarefas concluídas" in user_input.lower() and "mostrar" in user_input.lower():
            return True, self._process_natural_list_done_tasks()
        
        if "tarefas concluídas" in user_input.lower() and ("excluir" in user_input.lower() or "deletar" in user_input.lower() or "remover" in user_input.lower()):
            return True, self._process_natural_delete_done_tasks()
        
        if "quantas tarefas" in user_input.lower() or "contar tarefas" in user_input.lower():
            return True, self._process_natural_count_tasks()
        
        if "tarefas recentes" in user_input.lower() or "últimas tarefas" in user_input.lower():
            return True, self._process_natural_recent_tasks()
        
        # Se tiver o serviço Arcee, tenta processar como linguagem natural genérica
        if self.arcee_service:
            try:
                intent = self.arcee_service.detect_intent(user_input)
                
                if intent == "list_done_tasks":
                    return True, self._process_natural_list_done_tasks()
                    
                elif intent == "delete_done_tasks":
                    return True, self._process_natural_delete_done_tasks()
                    
                elif intent == "count_tasks":
                    return True, self._process_natural_count_tasks()
                    
                elif intent == "list_recent_tasks":
                    return True, self._process_natural_recent_tasks()
            
            except Exception as e:
                print(f"Erro ao processar linguagem natural com Arcee: {str(e)}")
                # Continua para processamento normal se falhar
        
        # Resposta padrão
        return False, "Comando não reconhecido. Use /help para ver os comandos disponíveis." 

    def _add_task(self, task_description: str) -> Tuple[bool, str]:
        """
        Adiciona uma nova tarefa ao Airtable.
        
        Args:
            task_description: Descrição da tarefa.
            
        Returns:
            Tupla contendo (sucesso, resposta).
        """
        try:
            # Prepara os dados da tarefa
            task_data = {
                "Name": task_description,
                "Status": "To Do",
                "Created": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Tenta adicionar a tarefa através do Veyrax
            result = self.veyrax_service.execute_tool(
                tool_name="airtable",
                method_name="create_record",
                parameters={
                    "base_id": self.base_id,
                    "table_name": self.table_name,
                    "fields": task_data
                }
            )
            
            if result.get("success"):
                record_id = result.get("id", "")
                return True, f"✅ Tarefa adicionada com ID: {record_id}"
            else:
                return False, f"❌ Erro ao adicionar tarefa: {result.get('error', 'Erro desconhecido')}"
                
        except Exception as e:
            print(f"Erro ao adicionar tarefa: {str(e)}")
            return False, f"❌ Erro ao adicionar tarefa: {str(e)}"
            
    def _complete_task(self, task_id: str) -> Tuple[bool, str]:
        """
        Marca uma tarefa como concluída.
        
        Args:
            task_id: ID da tarefa.
            
        Returns:
            Tupla contendo (sucesso, resposta).
        """
        try:
            # Prepara os dados para atualização
            update_data = {
                "Status": "Done",
                "Completed": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Tenta atualizar a tarefa através do Veyrax
            result = self.veyrax_service.execute_tool(
                tool_name="airtable",
                method_name="update_record",
                parameters={
                    "base_id": self.base_id,
                    "table_name": self.table_name,
                    "record_id": task_id,
                    "fields": update_data
                }
            )
            
            if result.get("success"):
                return True, f"✅ Tarefa {task_id} marcada como concluída!"
            else:
                return False, f"❌ Erro ao atualizar tarefa: {result.get('error', 'Erro desconhecido')}"
                
        except Exception as e:
            print(f"Erro ao completar tarefa: {str(e)}")
            return False, f"❌ Erro ao completar tarefa: {str(e)}"
            
    def _list_tasks(self) -> Tuple[bool, str]:
        """
        Lista todas as tarefas não concluídas.
        
        Returns:
            Tupla contendo (sucesso, resposta).
        """
        try:
            # Obtém as tarefas através do Veyrax
            result = self.veyrax_service.execute_tool(
                tool_name="airtable",
                method_name="list_records",
                parameters={
                    "base_id": self.base_id,
                    "table_name": self.table_name
                }
            )
            
            if not result.get("success"):
                return False, f"❌ Erro ao listar tarefas: {result.get('error', 'Erro desconhecido')}"
                
            records = result.get("records", [])
            
            # Filtra apenas tarefas não concluídas
            todo_tasks = [task for task in records if task.get("fields", {}).get("Status") != "Done"]
            
            if not todo_tasks:
                return True, "📋 Não há tarefas pendentes."
                
            # Formata a resposta
            response = "📋 Tarefas pendentes:\n\n"
            for task in todo_tasks:
                task_id = task.get("id", "")
                task_name = task.get("fields", {}).get("Name", "Sem nome")
                task_status = task.get("fields", {}).get("Status", "")
                response += f"• {task_id}: {task_name} [{task_status}]\n"
                
            return True, response
            
        except Exception as e:
            print(f"Erro ao listar tarefas: {str(e)}")
            return False, f"❌ Erro ao listar tarefas: {str(e)}"
            
    def _delete_task(self, task_id: str) -> Tuple[bool, str]:
        """
        Exclui uma tarefa.
        
        Args:
            task_id: ID da tarefa.
            
        Returns:
            Tupla contendo (sucesso, resposta).
        """
        try:
            # Tenta excluir a tarefa através do Veyrax
            result = self.veyrax_service.execute_tool(
                tool_name="airtable",
                method_name="delete_record",
                parameters={
                    "base_id": self.base_id,
                    "table_name": self.table_name,
                    "record_id": task_id
                }
            )
            
            if result.get("success"):
                return True, f"✅ Tarefa {task_id} excluída com sucesso!"
            else:
                return False, f"❌ Erro ao excluir tarefa: {result.get('error', 'Erro desconhecido')}"
                
        except Exception as e:
            print(f"Erro ao excluir tarefa: {str(e)}")
            return False, f"❌ Erro ao excluir tarefa: {str(e)}" 