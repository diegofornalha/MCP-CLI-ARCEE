#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para a API Arcee
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Carrega variáveis de ambiente
load_dotenv()

# Obtém a chave API
api_key = os.getenv("ARCEE_API_KEY")
model = os.getenv("ARCEE_MODEL") or "blitz"

print(f"Usando modelo: {model}")

# Configura o cliente OpenAI
client = OpenAI(api_key=api_key, base_url="https://models.arcee.ai/v1")

# Mensagem do sistema
system_message = {
    "role": "system",
    "content": "Você deve sempre responder em português do Brasil. Use uma linguagem natural e informal, mas profissional. Suas respostas devem ser claras, objetivas e culturalmente adequadas para o Brasil.",
}

# Mensagem do usuário
user_message = {
    "role": "user",
    "content": "Olá, você pode me ajudar?"
}

# Faz a requisição
print("Enviando requisição para a API Arcee...")
try:
    response = client.chat.completions.create(
        model=model,
        messages=[system_message, user_message],
        temperature=0.7,
    )
    
    print("\nResposta recebida:")
    print(f"Modelo: {response.model}")
    print(f"ID: {response.id}")
    
    # Extrai a resposta
    assistant_message = response.choices[0].message
    print(f"\nAssistente: {assistant_message.content}")
    
except Exception as e:
    print(f"Erro: {e}") 