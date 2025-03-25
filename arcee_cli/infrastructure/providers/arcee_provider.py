#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provedor de serviços do Arcee AI
"""

import os
import time
import json
from typing import Dict, List, Tuple, Union, Any
from dotenv import load_dotenv
from openai import OpenAI
from rich import print

# Carrega variáveis de ambiente
load_dotenv()


class ArceeProvider:
    """Provedor de serviços do Arcee AI"""

    def __init__(self):
        """Inicializa o provedor"""
        # Carrega variáveis de ambiente
        load_dotenv()

        # INVERSÃO DE PRIORIDADE: Agora prioriza a configuração sobre as variáveis de ambiente
        # Primeiro tenta carregar do arquivo de configuração
        self.api_key = self._load_api_key_from_config()

        # Se não encontrou na configuração, tenta das variáveis de ambiente
        if not self.api_key:
            self.api_key = os.getenv("ARCEE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "API key não encontrada. Defina ARCEE_API_KEY no .env ou configure com 'arcee configure'."
            )

        self.model = os.getenv("ARCEE_MODEL") or "auto"

        # Mensagem do sistema solicitando respostas em português
        self.system_message = {
            "role": "system",
            "content": "Você deve sempre responder em português do Brasil. Use uma linguagem natural e informal, mas profissional. Suas respostas devem ser claras, objetivas e culturalmente adequadas para o Brasil.",
        }

        # Configura o cliente OpenAI
        self.client = OpenAI(api_key=self.api_key, base_url="https://models.arcee.ai/v1")

    def _load_api_key_from_config(self) -> str:
        """Carrega a chave API do arquivo de configuração"""
        config_file = os.path.expanduser("~/.arcee/config.json")
        if not os.path.exists(config_file):
            return ""

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("api_key", "")
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {str(e)}")
            return ""

    def health_check(self) -> Tuple[bool, str]:
        """Verifica a saúde da API"""
        try:
            # Apenas verifica se temos uma chave API configurada
            if not self.api_key:
                return False, "Chave API não configurada"
            return True, "Chave API está configurada"
        except Exception as e:
            return False, f"Erro ao verificar configuração: {str(e)}"

    def generate_content_chat(
        self, messages: List[Dict[str, str]]
    ) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Gera conteúdo usando o chat"""
        try:
            if not self.api_key:
                return {"error": "Chave API não configurada"}

            # Registra apenas o tempo inicial sem exibir mensagem
            start_time = time.time()

            # Adiciona a mensagem do sistema no início se não estiver presente
            if not messages or messages[0].get("role") != "system":
                messages = [self.system_message] + messages

            # Faz a requisição usando o cliente OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )

            end_time = time.time()
            elapsed_time = end_time - start_time

            # Processa e retorna a resposta
            return self._process_response(response)

        except Exception as e:
            print(f"❌ Erro na chamada à API da Arcee: {e}")
            return {"error": str(e)}

    def _process_response(self, response) -> Dict[str, Any]:
        """
        Processa a resposta da API da Arcee

        Args:
            response: Resposta do cliente OpenAI

        Returns:
            Dict[str, Any]: Resposta processada
        """
        try:
            # Extrai o texto da resposta
            content = response.choices[0].message.content

            # Obtém metadados da resposta
            finish_reason = response.choices[0].finish_reason
            model_used = response.model

            # Formata a resposta
            processed_response = {
                "text": content,
                "finish_reason": finish_reason,
                "model": model_used,
                "selected_model": model_used,
                "raw_response": response,
            }

            return processed_response

        except Exception as e:
            print(f"❌ Erro ao processar resposta da Arcee: {e}")
            return {
                "text": "",
                "error": f"Falha ao processar resposta: {str(e)}",
                "raw_response": response,
            }

    def chat(self, mensagem: str, historico: List[Dict[str, str]] = None) -> str:
        """
        Processa uma mensagem de chat e retorna a resposta

        Args:
            mensagem: Mensagem do usuário
            historico: Histórico de mensagens anteriores

        Returns:
            str: Resposta da IA
        """
        try:
            # Inicializa o histórico se não fornecido
            if historico is None:
                historico = []

            # Adiciona a mensagem atual ao histórico
            mensagens = [self.system_message] + historico + [{"role": "user", "content": mensagem}]

            # Gera a resposta
            resposta = self.generate_content_chat(mensagens)

            if "error" in resposta:
                return f"❌ Erro: {resposta['error']}"

            return resposta["text"]

        except Exception as e:
            return f"❌ Erro: {str(e)}"
