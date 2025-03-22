#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar a integração com a API da Arcee

Este script demonstra como usar o cliente Arcee para
fazer requisições aos modelos da Arcee AI.
"""

import sys
import os
from dotenv import load_dotenv
from llm.providers.arcee_client import ArceeClient

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def testar_arcee():
    """Testa uma chamada para a API da Arcee"""
    # Verifica se a chave API está configurada
    api_key = os.getenv("ARCEE_API_KEY")
    if not api_key:
        print("❌ Erro: Variável de ambiente ARCEE_API_KEY não configurada.")
        print("   Verifique se o arquivo .env está configurado corretamente.")
        sys.exit(1)
    
    try:
        # Obtém o prompt do usuário ou usa um prompt padrão
        prompt = input("Digite seu prompt (ou pressione Enter para usar o padrão): ")
        if not prompt:
            prompt = "Explique as vantagens dos modelos da Arcee em comparação com o Gemini"
        
        # Seleciona o modelo (usuário pode especificar ou usar o padrão)
        modelo = input("Digite o modelo desejado (ou pressione Enter para usar virtuoso-large): ")
        if not modelo:
            modelo = "virtuoso-large"
        
        print(f"\n🔄 Enviando prompt para o modelo {modelo} da Arcee...")
        
        # Inicializa o cliente e faz a requisição
        cliente = ArceeClient(model=modelo)
        resposta = cliente.generate_content(prompt)
        
        # Verifica se houve erro
        if "error" in resposta and resposta["error"]:
            print(f"\n❌ Erro: {resposta['error']}")
            sys.exit(1)
        
        # Exibe a resposta
        print("\n✅ Resposta recebida com sucesso!")
        print("\n----- RESPOSTA DA ARCEE -----")
        print(resposta["text"])
        print("----- FIM DA RESPOSTA -----\n")
        
        # Exibe informações adicionais
        print(f"Modelo utilizado: {resposta.get('model', 'desconhecido')}")
        print(f"Motivo de finalização: {resposta.get('finish_reason', 'desconhecido')}")
        
        return resposta
    
    except Exception as e:
        print(f"\n❌ Erro não tratado: {e}")
        sys.exit(1)

def listar_modelos():
    """Lista os modelos disponíveis na Arcee"""
    try:
        cliente = ArceeClient()
        modelos = cliente.get_available_models()
        
        print("\n=== MODELOS DISPONÍVEIS NA ARCEE ===")
        for idx, modelo in enumerate(modelos, 1):
            print(f"{idx}. {modelo}")
        print("===================================\n")
    
    except Exception as e:
        print(f"\n❌ Erro ao listar modelos: {e}")

def main():
    """Função principal"""
    print("\n=== TESTE DE INTEGRAÇÃO COM A ARCEE ===\n")
    
    # Exibe os modelos disponíveis
    listar_modelos()
    
    # Testa a API
    testar_arcee()
    
    print("\n✨ Teste concluído com sucesso!")

if __name__ == "__main__":
    main() 