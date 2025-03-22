#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de interface de usuário do chat

Este módulo fornece a classe ChatUI para gerenciar a interface 
de usuário do chat, exibindo mensagens e obtendo entrada do usuário.
"""

class ChatUI:
    """Gerencia a interface de usuário do chat"""
    
    def __init__(self):
        """Inicializa a interface de usuário do chat"""
        self.prompt = "\n👤 Você: "
    
    def show_welcome_message(self, servers=None):
        """
        Exibe mensagem de boas-vindas
        
        Args:
            servers (list, optional): Lista de servidores MCP disponíveis
        """
        print("\n🤖 Chat Interativo com Arcee (modo 'auto') + Integração MCP iniciado!")
        print("   Digite 'sair', 'exit' ou 'quit' para encerrar o chat.")
        print("   Digite 'limpar' ou 'clear' para limpar o histórico.")
        if servers:
            print(f"   Servidores MCP disponíveis: {', '.join(servers)}\n")
    
    def get_user_input(self):
        """
        Obtém entrada do usuário
        
        Returns:
            str: Texto inserido pelo usuário
        """
        return input(self.prompt)
    
    def show_thinking(self):
        """Mostra indicador de processamento"""
        print("\n🔄 Processando...")
    
    def show_response(self, text):
        """
        Exibe resposta do assistente
        
        Args:
            text (str): Texto da resposta
        """
        print(f"\n🤖 Arcee: {text}")
    
    def show_model_info(self, response_data):
        """
        Exibe informações sobre o modelo utilizado
        
        Args:
            response_data (dict): Dados de resposta contendo informações do modelo
        """
        # Só exibe se tiver informações do modelo selecionado
        selected_model = response_data.get("selected_model")
        if selected_model:
            print(f"\n--- Informações do Modelo ---")
            print(f"Modelo selecionado: {selected_model}")
            
            if response_data.get("selection_reason"):
                print(f"Razão da seleção: {response_data.get('selection_reason')}")
            
            if response_data.get("task_type"):
                print(f"Tipo de tarefa: {response_data.get('task_type')}")
            
            if response_data.get("domain"):
                print(f"Domínio: {response_data.get('domain')}")
            
            if response_data.get("complexity"):
                print(f"Complexidade: {response_data.get('complexity')}")
            
            print(f"Modelo usado: {response_data.get('model', 'desconhecido')}")
            print("-----------------------------")
    
    def show_error(self, error_message):
        """
        Exibe mensagem de erro
        
        Args:
            error_message (str): Mensagem de erro
        """
        print(f"\n❌ Erro: {error_message}")
    
    def show_warning(self, warning_message):
        """
        Exibe mensagem de aviso
        
        Args:
            warning_message (str): Mensagem de aviso
        """
        print(f"\n⚠️ Aviso: {warning_message}")
    
    def show_servers_list(self, servers):
        """
        Exibe lista de servidores disponíveis
        
        Args:
            servers (list): Lista de servidores
        """
        print(f"\n📋 Servidores MCP disponíveis: {', '.join(servers)}")
    
    def show_goodbye(self):
        """Exibe mensagem de despedida"""
        print("\n👋 Encerrando chat. Até a próxima!")
    
    def show_history_cleared(self):
        """Exibe confirmação de limpeza do histórico"""
        print("\n🧹 Histórico de chat limpo!\n") 