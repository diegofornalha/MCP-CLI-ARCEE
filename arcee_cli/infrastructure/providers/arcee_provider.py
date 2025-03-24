#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provedor de serviços do Arcee AI
"""

import json
import os
from typing import Dict, List, Tuple, Union

import requests
from rich import print


class ArceeProvider:
    """Provedor de serviços do Arcee AI"""

    def __init__(self):
        """Inicializa o provedor"""
        self.config_file = os.path.expanduser("~/.arcee/config.json")
        self.config = self._load_config()
        self.api_key = self.config.get("api_key", "")
        self.api_url = "https://models.arcee.ai"
        self.model = "gpt-4"
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
            response = self.session.get(
                f"{self.api_url}/health",
                timeout=10,
            )
            response.raise_for_status()
            return True, "API está funcionando normalmente"
        except requests.exceptions.RequestException as e:
            return False, f"Erro ao conectar com a API: {str(e)}"

    def generate_content_chat(
        self, messages: List[Dict[str, str]]
    ) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Gera conteúdo usando o chat"""
        try:
            response = self.session.post(
                f"{self.api_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "stream": False,
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro ao gerar conteúdo: {str(e)}"}
        except Exception as e:
            return {"error": f"Erro inesperado: {str(e)}"}
