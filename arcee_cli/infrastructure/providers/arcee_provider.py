#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provedor de serviços do Arcee AI
"""

import json
import os
from typing import Dict, List, Tuple, Union
from dotenv import load_dotenv

import requests
from rich import print

# Carrega variáveis de ambiente
load_dotenv()


class ArceeProvider:
    """Provedor de serviços do Arcee AI"""

    def __init__(self):
        """Inicializa o provedor"""
        self.config_file = os.path.expanduser("~/.arcee/config.json")
        self.config = self._load_config()

        # Prioriza variáveis de ambiente sobre arquivo de configuração
        self.api_key = os.getenv("ARCEE_API_KEY") or self.config.get("api_key", "")
        self.model = os.getenv("ARCEE_MODEL") or "auto"
        self.api_url = "https://models.arcee.ai"
        self.api_version = "v1"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "arcee-cli/1.0.0",
        }

        if self.config.get("org"):
            self.headers["X-Arcee-Org"] = self.config["org"]

        # Criar uma sessão para reutilizar conexões
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _load_config(self) -> Dict:
        """Carrega a configuração do arquivo"""
        if not os.path.exists(self.config_file):
            return {}

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {str(e)}")
            return {}

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

            # Faz a requisição para a API
            url = f"{self.api_url}/{self.api_version}/chat/completions"

            response = self.session.post(
                url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
                timeout=30,
            )

            # Verifica se houve erro na requisição
            response.raise_for_status()

            # Retorna a resposta da API
            return response.json()

        except requests.exceptions.RequestException as e:
            return {"error": f"Erro na requisição: {str(e)}"}
        except Exception as e:
            return {"error": f"Erro inesperado: {str(e)}"}
