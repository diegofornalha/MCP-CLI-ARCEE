#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste do cliente oficial Arcee usando OpenAI
"""

import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

# Força a recarga do arquivo .env
load_dotenv(find_dotenv(), override=True)


def main():
    """Função principal"""
    print("\n=== TESTE DO CLIENTE OFICIAL ARCEE ===\n")

    # Verifica se temos a chave API
    api_key = os.getenv("ARCEE_API_KEY")
    if not api_key:
        print("❌ Erro: ARCEE_API_KEY não encontrada no ambiente")
        return

    print(f"🔍 Debug - API Key carregada: {api_key}")

    try:
        print("🔄 Gerando texto...\n")

        # Configura o cliente OpenAI com a URL base do Arcee Conductor
        client = OpenAI(api_key=api_key, base_url="https://models.arcee.ai/v1")

        # Faz a requisição usando o cliente OpenAI
        response = client.chat.completions.create(
            model="auto",
            messages=[{"role": "user", "content": "Olá! Como você está?"}],
            temperature=0.7,
        )

        print("\n✅ Resposta recebida:")
        print(response)

    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")


if __name__ == "__main__":
    main()
