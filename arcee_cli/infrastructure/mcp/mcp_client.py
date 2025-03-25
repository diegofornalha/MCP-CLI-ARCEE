#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente MCP do Arcee usando FastAPI
"""

from typing import Dict, Any, Tuple, Optional
import json
import os
import requests
from dotenv import load_dotenv


class MCPClient:
    """Cliente MCP do Arcee"""

    def __init__(self):
        """Inicializa o cliente MCP"""
        load_dotenv()

        # Tenta obter a chave API
        self.api_key = os.getenv("VEYRAX_API_KEY")
        if not self.api_key:
            # Tenta carregar da configuração do Cursor
            cursor_config = os.path.expanduser("~/.cursor/config.json")
            if os.path.exists(cursor_config):
                try:
                    with open(cursor_config) as f:
                        config = json.load(f)
                        self.api_key = config.get("veyraxApiKey")
                        # Também pega a porta do MCP se estiver configurada
                        self.port = config.get("mcpPort", 8081)
                except:
                    pass

        if not self.api_key:
            raise ValueError("Chave API não encontrada")

        # Usa a porta da variável de ambiente se disponível, senão usa a do config ou o padrão
        self.port = int(os.getenv("MCP_PORT", str(getattr(self, "port", 8081))))
        self.base_url = f"http://localhost:{self.port}"

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Any]:
        """Faz uma requisição HTTP para o servidor MCP"""
        try:
            headers = {"Content-Type": "application/json", "X-API-Key": self.api_key}

            url = f"{self.base_url}{endpoint}"
            print(f"🔄 Fazendo requisição {method} para {url}")

            if method == "GET":
                response = requests.get(url, headers=headers)
            else:
                print(f"📤 Enviando dados: {json.dumps(data, indent=2)}")
                response = requests.post(url, headers=headers, json=data)

            response.raise_for_status()

            # Processa a resposta
            try:
                result = response.json()
                print(f"📥 Resposta recebida: {json.dumps(result, indent=2)}")
                return True, result
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar resposta JSON: {e}")
                print(f"📄 Conteúdo da resposta: {response.text}")
                return False, f"Erro ao processar resposta: {str(e)}"

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return False, str(e)
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False, str(e)

    def get_tools(self) -> Tuple[bool, Any]:
        """Lista todas as ferramentas disponíveis"""
        return self._make_request("GET", "/tools")

    def tool_call(
        self, tool: str, method: str, parameters: Dict[str, Any] = None
    ) -> Tuple[bool, Any]:
        """Executa uma ferramenta específica"""
        data = {"tool": tool, "method": method, "parameters": parameters or {}}
        return self._make_request("POST", "/tool_call", data)
