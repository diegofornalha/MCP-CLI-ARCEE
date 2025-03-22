#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chat Interativo com a Arcee

Este script implementa um chat interativo de linha de comando
usando o cliente Arcee no modo 'auto', onde o melhor modelo
é selecionado automaticamente para cada mensagem.
"""

import sys
import os
from dotenv import load_dotenv
from llm.providers.arcee_client import ArceeClient

# Carrega variáveis de ambiente
load_dotenv()

class ChatArcee:
    """Implementação de chat interativo com a Arcee"""
    
    def __init__(self):
        """Inicializa o chat com a Arcee"""
        # Verifica se a chave API está configurada
        api_key = os.getenv("ARCEE_API_KEY")
        if not api_key:
            print("❌ Erro: Variável de ambiente ARCEE_API_KEY não configurada.")
            print("   Verifique se o arquivo .env está configurado corretamente.")
            sys.exit(1)
        
        try:
            # Inicializa o cliente Arcee com modo auto
            self.client = ArceeClient(model="auto")
            self.history = []
            print("\n🤖 Chat Interativo com Arcee (modo 'auto') iniciado!")
            print("   Digite 'sair', 'exit' ou 'quit' para encerrar o chat.")
            print("   Digite 'limpar' ou 'clear' para limpar o histórico.\n")
        except Exception as e:
            print(f"❌ Erro ao inicializar cliente Arcee: {e}")
            sys.exit(1)
    
    def add_to_history(self, role: str, content: str):
        """Adiciona uma mensagem ao histórico do chat"""
        self.history.append({"role": role, "content": content})
    
    def clear_history(self):
        """Limpa o histórico do chat"""
        self.history = []
        print("\n🧹 Histórico de chat limpo!\n")
    
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
            
            # Adiciona a resposta ao histórico
            self.add_to_history("assistant", response["text"])
            
            # Retorna a resposta formatada
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
                
                # Envia a mensagem e recebe a resposta
                print("\n🔄 Processando...")
                response = self.send_message(user_input)
                
                if response:
                    # Exibe a resposta
                    print(f"\n🤖 Arcee: {response['text']}")
                    
                    # Exibe informações sobre o modelo
                    self.show_model_info(response)
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrompido pelo usuário. Até a próxima!")
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            sys.exit(1)

def main():
    """Função principal"""
    print("\n=== CHAT INTERATIVO COM ARCEE ===\n")
    
    # Inicializa e executa o chat
    chat = ChatArcee()
    chat.run()

if __name__ == "__main__":
    main() 