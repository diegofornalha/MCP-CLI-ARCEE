#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arcee CLI - Interface de linha de comando para o Arcee AI
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from .arcee_client import ArceeClient

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def test_connection(args):
    """Testa a conexão com o modelo Arcee AI"""
    try:
        print("Testando conexão com o modelo Arcee AI...")
        
        # Verificar a configuração da API key no ambiente
        api_key = os.getenv("ARCEE_API_KEY")
        print(f"API key configurada: {bool(api_key)}")
        print(f"Primeiros 5 caracteres da API key: {api_key[:5] if api_key else 'AUSENTE'}")
        
        client = ArceeClient()
        print(f"Cliente Arcee inicializado com URL: {client.api_url}")
        print(f"Modelo configurado: {client.model}")
        
        print("Iniciando health check...")
        status, message = client.health_check()
        
        if status:
            print(f"✅ {message}")
            print("Agora testando geração de conteúdo simples...")
            
            response = client.generate_content("Olá, você pode me ouvir?")
            if "error" not in response:
                print(f"✅ Geração de conteúdo funcionando!")
                print(f"Modelo usado: {response.get('model', 'desconhecido')}")
                print(f"Resposta: {response.get('text')[:100]}...")
            else:
                print(f"❌ Erro na geração de conteúdo: {response.get('error')}")
        else:
            print(f"❌ {message}")
            
    except Exception as e:
        print(f"❌ Erro ao testar conexões: {str(e)}")
        import traceback
        print(f"Detalhes do erro: {traceback.format_exc()}")

def chat_with_arcee(args):
    """Inicia uma conversa com o modelo Arcee AI"""
    try:
        client = ArceeClient()
        
        print("\n🤖 Iniciando chat com Arcee AI. Digite 'sair' para encerrar.\n")
        
        context = []
        
        while True:
            user_input = input("\n👤 Você: ")
            
            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\n👋 Encerrando chat. Até logo!")
                break
            
            # Adiciona a mensagem do usuário ao contexto
            context.append({"role": "user", "content": user_input})
            
            # Obtém resposta do modelo
            response = client.generate_content_chat(context)
            
            # Verifica se houve erro
            if "error" in response:
                print(f"\n❌ Erro: {response['error']}")
                continue
            
            # Exibe a resposta
            ai_response = response["text"]
            print(f"\n🤖 Arcee: {ai_response}")
            
            # Adiciona a resposta do modelo ao contexto
            context.append({"role": "assistant", "content": ai_response})
            
            # Limita o contexto para evitar tokens excessivos
            if len(context) > 10:
                # Mantém apenas as últimas 10 mensagens
                context = context[-10:]
                
    except Exception as e:
        print(f"\n❌ Erro ao iniciar chat com Arcee: {str(e)}")

def main():
    """Função principal do CLI"""
    parser = argparse.ArgumentParser(description="Arcee CLI - Interface de linha de comando para Arcee AI")
    parser.add_argument("--version", action="version", version="Arcee CLI v1.0.0")
    parser.add_argument("--config", help="Arquivo de configuração")
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Comando: teste
    parser_test = subparsers.add_parser("teste", help="Testa a conexão com a API do Arcee")
    
    # Comando: chat
    parser_chat = subparsers.add_parser("chat", help="Inicia uma conversa com o modelo")
    
    args = parser.parse_args()
    
    # Se nenhum comando foi especificado, mostra a ajuda
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Executa o comando especificado
    commands = {
        "teste": test_connection,
        "chat": chat_with_arcee
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"Comando desconhecido: {args.command}")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 