#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente para comunicação com a API do Arcee AI
"""

import os
import requests
from typing import Dict, List, Tuple, Optional

class ArceeClient:
    """Cliente para comunicação com a API do Arcee AI"""
    
    def __init__(self):
        """Inicializa o cliente com configurações do ambiente"""
        self.api_key = os.getenv("ARCEE_API_KEY")
        if not self.api_key:
            raise ValueError("ARCEE_API_KEY não encontrada nas variáveis de ambiente")
            
        self.api_url = os.getenv("ARCEE_API_URL", "https://api.arcee.ai")
        self.model = os.getenv("ARCEE_MODEL", "arcee-large")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def health_check(self) -> Tuple[bool, str]:
        """Verifica a saúde da API"""
        try:
            response = requests.get(
                f"{self.api_url}/health",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True, "Conexão estabelecida com sucesso"
        except requests.exceptions.RequestException as e:
            return False, f"Erro na conexão: {str(e)}"
    
    def generate_content(self, prompt: str) -> Dict:
        """Gera conteúdo a partir de um prompt"""
        try:
            response = requests.post(
                f"{self.api_url}/v1/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_tokens": 1000
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro na requisição: {str(e)}"}
    
    def generate_content_chat(self, messages: List[Dict[str, str]]) -> Dict:
        """Gera conteúdo em formato de chat"""
        try:
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 1000
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro na requisição: {str(e)}"} 