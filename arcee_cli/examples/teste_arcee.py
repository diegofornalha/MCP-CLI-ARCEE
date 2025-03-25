#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para a API Arcee
"""

import os
import sys
import logging
from typing import Dict, List, Any
from dotenv import load_dotenv
from openai import OpenAI
import json

# Tenta importar o módulo de logging se estiver disponível
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from arcee_cli.infrastructure.logging_config import configurar_logging, obter_logger, configurar_loggers_bibliotecas
    # Configura o logger
    configurar_logging()
    logger = obter_logger("teste_arcee")
    
    # Configura loggers de bibliotecas para remover mensagens HTTP
    configurar_loggers_bibliotecas()
    print("✅ Sistema de logging configurado")
except ImportError:
    # Configura um logger básico se o módulo não estiver disponível
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )
    logger = logging.getLogger("teste_arcee")
    
    # Configura manualmente o logger do OpenAI para suprimir mensagens HTTP
    logging.getLogger("openai").setLevel(logging.WARNING)
    print("✅ Logger básico configurado")

# Carrega variáveis de ambiente
load_dotenv()

# Obtém a chave API
api_key = os.getenv("ARCEE_API_KEY")
model = os.getenv("ARCEE_MODEL") or "blitz"

logger.info(f"Usando modelo: {model}")
print(f"Usando modelo: {model}")

# Configura o cliente OpenAI
client = OpenAI(api_key=api_key, base_url="https://models.arcee.ai/v1")

# Mensagem do sistema
system_message: Dict[str, str] = {
    "role": "system",
    "content": "Você deve sempre responder em português do Brasil. Use uma linguagem natural e informal, mas profissional. Suas respostas devem ser claras, objetivas e culturalmente adequadas para o Brasil.",
}

# Mensagem do usuário
user_message: Dict[str, str] = {
    "role": "user",
    "content": "Olá, você pode me ajudar?"
}

# Faz a requisição
logger.info("Enviando requisição para a API Arcee...")
print("Enviando requisição para a API Arcee...")
try:
    # Criamos uma lista explicitamente tipada
    messages: List[Dict[str, str]] = [system_message, user_message]
    logger.debug(f"Mensagens enviadas: {messages}")
    
    # Usamos o type ignore para ignorar o erro de tipo conhecido
    response = client.chat.completions.create(  # type: ignore
        model=model,
        messages=messages,
        temperature=0.7,
    )
    
    logger.info("Resposta recebida com sucesso")
    print("\nResposta recebida:")
    print(f"Modelo: {response.model}")
    print(f"ID: {response.id}")
    
    # Extrai a resposta
    assistant_message = response.choices[0].message
    content = assistant_message.content or ""  # Garante que content nunca será None
    logger.info(f"Resposta do assistente recebida: {len(content)} caracteres")
    print(f"\nAssistente: {assistant_message.content}")
    
except Exception as e:
    logger.error(f"Erro ao fazer requisição: {e}")
    print(f"Erro: {e}") 