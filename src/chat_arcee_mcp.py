#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chat Interativo com Arcee e integração MCP

Este script implementa um chat interativo de linha de comando
usando o cliente Arcee no modo 'auto' integrado com ferramentas MCP.
"""

import sys
import os
import re
import json
import datetime
from dotenv import load_dotenv

# Adiciona o diretório src ao caminho de importação
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.providers.arcee_client import ArceeClient
from src.mcp.integrations import MCPIntegration, AirtableIntegration

# Carrega variáveis de ambiente
load_dotenv()

class ChatArceeMCP:
    """Implementação de chat interativo com Arcee e MCP"""
    
    def __init__(self):
        """Inicializa o chat com Arcee e MCP"""
        # Verifica se a chave API está configurada
        api_key = os.getenv("ARCEE_API_KEY")
        if not api_key:
            print("❌ Erro: Variável de ambiente ARCEE_API_KEY não configurada.")
            print("   Verifique se o arquivo .env está configurado corretamente.")
            sys.exit(1)
        
        try:
            # Inicializa o cliente Arcee com modo auto
            self.client = ArceeClient(model="auto")
            
            # Inicializa as integrações MCP
            self.mcp_integration = MCPIntegration()
            self.airtable = AirtableIntegration()
            
            # Estado do chat
            self.history = []
            self.available_servers = self.mcp_integration.list_available_servers()
            
            # Instruções do sistema
            self.system_instruction = (
                "Você é um assistente com acesso a ferramentas MCP. Quando o usuário pedir algo relacionado "
                "a criar tarefas no Airtable, use o formato especial: "
                "[[AIRTABLE_CREATE_TASK: nome_da_tarefa | descrição | data_limite | status]]. "
                "Quando precisar listar tarefas, use: [[AIRTABLE_LIST_TASKS]]. "
                "Responda sempre em português brasileiro."
            )
            
            # Adiciona instrução do sistema
            self.add_to_history("system", self.system_instruction)
            
            # Mensagem de boas-vindas
            print("\n🤖 Chat Interativo com Arcee (modo 'auto') + Integração MCP iniciado!")
            print("   Digite 'sair', 'exit' ou 'quit' para encerrar o chat.")
            print("   Digite 'limpar' ou 'clear' para limpar o histórico.")
            print(f"   Servidores MCP disponíveis: {', '.join(self.available_servers)}\n")
        
        except Exception as e:
            print(f"❌ Erro ao inicializar: {e}")
            sys.exit(1)
    
    def add_to_history(self, role: str, content: str):
        """Adiciona uma mensagem ao histórico do chat"""
        self.history.append({"role": role, "content": content})
    
    def clear_history(self):
        """Limpa o histórico do chat"""
        # Preserva a instrução do sistema
        system_message = self.history[0] if self.history and self.history[0]["role"] == "system" else None
        
        self.history = []
        if system_message:
            self.history.append(system_message)
        
        print("\n🧹 Histórico de chat limpo!\n")
    
    def process_special_commands(self, text: str) -> str:
        """
        Processa comandos especiais no texto
        
        Args:
            text (str): Texto que pode conter comandos especiais
            
        Returns:
            str: Texto processado com os resultados dos comandos
        """
        # Verifica se há comandos do Airtable
        
        # Criar tarefa
        create_task_pattern = r"\[\[AIRTABLE_CREATE_TASK: ([^|]+)\|([^|]*)\|([^|]*)\|([^]]*)\]\]"
        
        while re.search(create_task_pattern, text):
            match = re.search(create_task_pattern, text)
            if match:
                task_name = match.group(1).strip()
                description = match.group(2).strip() if match.group(2).strip() else None
                deadline = match.group(3).strip() if match.group(3).strip() else None
                status = match.group(4).strip() if match.group(4).strip() else "Not started"
                
                # Cria a tarefa
                result = self.airtable.create_task(task_name, description, deadline, status)
                
                # Prepara a resposta
                if "error" in result:
                    response = f"🔴 Erro ao criar tarefa: {result['error']}"
                else:
                    response = f"✅ Tarefa '{task_name}' criada com sucesso!"
                
                # Substitui o comando pelo resultado
                text = text.replace(match.group(0), response)
        
        # Listar tarefas
        if "[[AIRTABLE_LIST_TASKS]]" in text:
            # Obtém as tarefas
            result = self.airtable.list_tasks()
            
            # Prepara a resposta
            if "error" in result:
                response = f"🔴 Erro ao listar tarefas: {result['error']}"
            else:
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
            
            # Substitui o comando pelo resultado
            text = text.replace("[[AIRTABLE_LIST_TASKS]]", response)
        
        return text
    
    def send_message(self, message: str):
        """Envia uma mensagem para o modelo e retorna a resposta"""
        # Adiciona a mensagem do usuário ao histórico
        self.add_to_history("user", message)
        
        try:
            # Cria uma cópia do histórico para enviar ao modelo
            messages = self.history.copy()
            
            # Envia a mensagem para o modelo
            response = self.client.generate_content_chat(messages)
            
            # Verifica se houve erro
            if "error" in response and response["error"]:
                print(f"\n❌ Erro: {response['error']}")
                return None
            
            # Processa comandos especiais
            processed_text = self.process_special_commands(response["text"])
            
            # Atualiza o texto processado
            response["processed_text"] = processed_text
            
            # Adiciona a resposta ao histórico (usando o texto original para manter a consistência)
            self.add_to_history("assistant", response["text"])
            
            # Retorna a resposta
            return response
        
        except Exception as e:
            print(f"\n❌ Erro ao processar mensagem: {e}")
            return None
    
    def show_model_info(self, response):
        """Exibe informações sobre o modelo utilizado"""
        # Só exibe se tiver informações do modelo selecionado
        selected_model = response.get("selected_model")
        if selected_model:
            print(f"\n--- Informações do Modelo ---")
            print(f"Modelo selecionado: {selected_model}")
            
            if response.get("selection_reason"):
                print(f"Razão da seleção: {response.get('selection_reason')}")
            
            if response.get("task_type"):
                print(f"Tipo de tarefa: {response.get('task_type')}")
            
            if response.get("domain"):
                print(f"Domínio: {response.get('domain')}")
            
            if response.get("complexity"):
                print(f"Complexidade: {response.get('complexity')}")
            
            print(f"Modelo usado: {response.get('model', 'desconhecido')}")
            print("-----------------------------")
    
    def run(self):
        """Executa o loop principal do chat"""
        try:
            while True:
                # Obtém a mensagem do usuário
                user_input = input("\n👤 Você: ")
                
                # Verifica comandos especiais
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    print("\n👋 Encerrando chat. Até a próxima!")
                    break
                
                if user_input.lower() in ['limpar', 'clear']:
                    self.clear_history()
                    continue
                
                if not user_input.strip():
                    continue
                
                # Verifica comandos de MCP
                if user_input.lower() == "mcp list":
                    print(f"\n📋 Servidores MCP disponíveis: {', '.join(self.available_servers)}")
                    continue
                
                # Envia a mensagem e recebe a resposta
                print("\n🔄 Processando...")
                response = self.send_message(user_input)
                
                if response:
                    # Exibe a resposta (texto processado)
                    print(f"\n🤖 Arcee: {response.get('processed_text', response['text'])}")
                    
                    # Exibe informações sobre o modelo
                    self.show_model_info(response)
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrompido pelo usuário. Até a próxima!")
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            sys.exit(1)

def main():
    """Função principal"""
    print("\n=== CHAT INTERATIVO COM ARCEE + MCP ===\n")
    
    # Inicializa e executa o chat
    chat = ChatArceeMCP()
    chat.run()

if __name__ == "__main__":
    main() 