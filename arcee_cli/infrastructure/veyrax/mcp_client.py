#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente MCP do Arcee usando FastAPI
"""

from typing import Dict, Any, Tuple, Optional, List
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

    def save_memory(self, memory: str, tool: str) -> bool:
        """Salva uma memória via MCP"""
        request = {
            "tool": "veyrax",
            "method": "save_memory",
            "parameters": {"memory": memory, "tool": tool},
        }

        result = self._execute_command(request)
        return result is not None and result.get("data", {}).get("success", False)

    def get_memories(
        self, tool: Optional[str] = None, limit: int = 10, offset: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Obtém memórias via MCP com suporte a paginação e filtragem por ferramenta.

        Args:
            tool: Nome da ferramenta para filtrar (opcional)
            limit: Número máximo de memórias a retornar
            offset: Número de memórias a pular

        Returns:
            Dict com as memórias ou None em caso de erro
        """
        params = {"limit": limit, "offset": offset}
        if tool:
            params["tool"] = tool

        request = {"tool": "veyrax", "method": "get_memory", "parameters": params}

        result = self._execute_command(request)
        return result.get("data") if result else None

    def update_memory(self, memory_id: str, memory: str, tool: str) -> bool:
        """
        Atualiza uma memória existente via MCP.

        Args:
            memory_id: ID da memória a ser atualizada
            memory: Novo conteúdo da memória
            tool: Nome da ferramenta associada

        Returns:
            bool indicando sucesso da operação
        """
        request = {
            "tool": "veyrax",
            "method": "update_memory",
            "parameters": {"id": memory_id, "memory": memory, "tool": tool},
        }

        result = self._execute_command(request)
        return result is not None and result.get("data", {}).get("success", False)

    def delete_memory(self, memory_id: str) -> bool:
        """
        Deleta uma memória via MCP.

        Args:
            memory_id: ID da memória a ser deletada

        Returns:
            bool indicando sucesso da operação
        """
        request = {
            "tool": "veyrax",
            "method": "delete_memory",
            "parameters": {"id": memory_id},
        }

        result = self._execute_command(request)
        return result is not None and result.get("data", {}).get("success", False)
