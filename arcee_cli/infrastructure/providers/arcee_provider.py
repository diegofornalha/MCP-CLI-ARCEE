#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provedor de serviços do Arcee AI
"""

import os
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

        # Prioriza variáveis de ambiente sobre arquivo de configuração
        self.api_key = os.getenv("ARCEE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key não encontrada. Defina ARCEE_API_KEY no .env ou passe como parâmetro."
            )

        print(f"\n🔍 Debug - API Key: {self.api_key[:10]}...")
        self.model = os.getenv("ARCEE_MODEL") or "auto"

        # Mensagem do sistema solicitando respostas em português
        self.system_message = {
            "role": "system",
            "content": "Você deve sempre responder em português do Brasil. Use uma linguagem natural e informal, mas profissional. Suas respostas devem ser claras, objetivas e culturalmente adequadas para o Brasil.",
        }

        # Configura o cliente OpenAI
        self.client = OpenAI(
            api_key=self.api_key, base_url="https://models.arcee.ai/v1"
        )

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

            # Adiciona a mensagem do sistema no início se não estiver presente
            if not messages or messages[0].get("role") != "system":
                messages = [self.system_message] + messages

            # Faz a requisição usando o cliente OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )

            # Processa e retorna a resposta
            return self._process_response(response)

        except Exception as e:
            print(f"Erro na chamada à API da Arcee: {e}")
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
            print(f"Erro ao processar resposta da Arcee: {e}")
            return {
                "text": "",
                "error": f"Falha ao processar resposta: {str(e)}",
                "raw_response": response,
            }
