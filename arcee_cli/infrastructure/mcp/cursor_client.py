#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente Cursor do Arcee usando FastAPI
"""

from typing import Dict, Any, Tuple, Optional, List
import json
import os
import requests
from dotenv import load_dotenv
import logging

# Configura logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CursorClient:
    """Cliente para comunicação com o MCP"""

    def __init__(self):
        """Inicializa o cliente"""
        self.logger = logging.getLogger(__name__)
        # Obtém a porta do ambiente ou usa 8082 como padrão
        self.port = os.environ.get("MCP_PORT", "8082")
        self.base_url = f"http://localhost:{self.port}"

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
                except Exception as e:
                    logger.error(f"Erro ao carregar config: {e}")
                    pass

        if not self.api_key:
            raise ValueError("Chave API não encontrada")

        # Usa a porta da variável de ambiente se disponível, senão usa a do config ou o padrão
        self.port = int(os.getenv("MCP_PORT", str(getattr(self, "port", 8081))))
        self.base_url = f"http://localhost:{self.port}"

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Faz uma requisição HTTP para o servidor MCP"""
        try:
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
                "User-Agent": "Arcee-CLI/1.0",
            }

            url = f"{self.base_url}{endpoint}"
            logger.debug(f"Fazendo requisição {method} para {url}")

            if method == "GET":
                response = requests.get(url, headers=headers)
            else:
                logger.debug(f"Enviando dados: {json.dumps(data, indent=2)}")
                response = requests.post(url, headers=headers, json=data)

            response.raise_for_status()

            # Processa a resposta
            try:
                result = response.json()
                logger.debug(f"Resposta recebida: {json.dumps(result, indent=2)}")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar resposta JSON: {e}")
                logger.error(f"Conteúdo da resposta: {response.text}")
                return {"error": f"Erro ao processar resposta: {str(e)}"}

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return {"error": str(e)}

    def get_tools(self) -> Dict[str, Any]:
        """Lista todas as ferramentas disponíveis"""
        return self._make_request("GET", "/tools")

    def tool_call(
        self, tool: str, method: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Executa uma ferramenta específica"""
        data = {"tool": tool, "method": method, "parameters": parameters or {}}
        return self._make_request("POST", "/tool_call", data)

    def save_memory(self, memory: str, tool: str) -> Dict[str, Any]:
        """Salva uma memória no VeyraX"""
        return self.tool_call("veyrax", "save_memory", {"memory": memory, "tool": tool})

    def get_memories(
        self, tool: Optional[str] = None, limit: int = 10, offset: int = 0
    ) -> Dict[str, Any]:
        """Obtém memórias do VeyraX"""
        params = {}
        if tool:
            params["tool"] = tool
        params["limit"] = limit
        params["offset"] = offset
        return self.tool_call("veyrax", "get_memory", params)

    def update_memory(self, memory_id: str, memory: str, tool: str) -> Dict[str, Any]:
        """Atualiza uma memória existente"""
        return self.tool_call(
            "veyrax", "update_memory", {"id": memory_id, "memory": memory, "tool": tool}
        )

    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Deleta uma memória"""
        return self.tool_call("veyrax", "delete_memory", {"id": memory_id})

    def query_cursor_agent(self, query: str) -> Dict[str, Any]:
        """Envia uma consulta para o Cursor Agent"""
        return self.tool_call("cursor_agent", "query", {"query": query})
