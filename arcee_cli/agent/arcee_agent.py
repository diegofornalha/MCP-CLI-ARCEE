#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agente automatizado para o Arcee CLI
"""

import json
import subprocess
from typing import Dict, Any, List, Tuple, Optional
from arcee_cli.infrastructure.mcp.mcp_client import MCPClient


class ArceeAgent:
    """
    Agente automatizado para o Arcee CLI
    """

    def __init__(self):
        """
        Inicializa o agente automatizado
        """
        self.last_error = None
        self.mcp_client = MCPClient()

    def get_tools(self) -> Tuple[bool, Any]:
        """
        Obtém a lista de ferramentas disponíveis

        Returns:
            Tuple[bool, Any]: Tupla com (sucesso, resultado)
        """
        try:
            return self.mcp_client.get_tools()
        except Exception as e:
            self.last_error = f"Erro ao obter ferramentas: {e}"
            return False, {"error": self.last_error}

    def tool_call(
        self, tool_name: str, method_name: str, params: Dict[str, Any] = None
    ) -> Tuple[bool, Any]:
        """
        Executa uma ferramenta específica

        Args:
            tool_name: Nome da ferramenta
            method_name: Nome do método
            params: Parâmetros para o método (opcional)

        Returns:
            Tuple[bool, Any]: Tupla com (sucesso, resultado)
        """
        try:
            return self.mcp_client.tool_call(tool_name, method_name, params)
        except Exception as e:
            self.last_error = f"Erro ao executar ferramenta: {e}"
            return False, {"error": self.last_error}

    def process_user_command(self, user_input: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Processa um comando do usuário

        Args:
            user_input: Comando do usuário

        Returns:
            Tuple[bool, Dict[str, Any]]: Tupla com (sucesso, resultado)
        """
        # Verifica se é um comando para listar ferramentas
        if user_input.lower() in ["ferramentas", "tools"]:
            success, tools = self.get_tools()

            if not success:
                return False, {"error": "Não foi possível obter a lista de ferramentas"}

            # Formata as ferramentas para exibição
            formatted_tools = {}
            for tool_name, tool_info in tools.items():
                formatted_tools[tool_name] = {
                    "description": tool_info.get("description", "Sem descrição"),
                    "methods": list(tool_info.get("methods", {}).keys()),
                }

            return True, {"result": formatted_tools}

        # Verifica se é um comando para chamar uma ferramenta
        parts = user_input.split(maxsplit=2)
        if len(parts) >= 2:
            tool_name = parts[0]
            method_name = parts[1]

            # Verifica se há parâmetros
            params = {}
            if len(parts) > 2:
                try:
                    params = json.loads(parts[2])
                except json.JSONDecodeError:
                    return False, {
                        "error": f"Parâmetros inválidos: {parts[2]}. Use formato JSON válido."
                    }

            # Executa a ferramenta
            success, result = self.tool_call(tool_name, method_name, params)

            if not success:
                return False, {
                    "error": f"Erro ao executar {tool_name}.{method_name}: {result}"
                }

            return True, {"result": result}

        # Se não for um comando reconhecido
        return False, {
            "error": "Comando não reconhecido. Use 'ferramentas' para listar as ferramentas disponíveis ou '<ferramenta> <método> [parâmetros]' para executar."
        }


# Agente global para ser reutilizado
_agent = None


def get_agent() -> Optional[ArceeAgent]:
    """Obtém uma instância do agente global ou cria um novo se não existir"""
    global _agent
    if _agent is None:
        try:
            _agent = ArceeAgent()
        except Exception as e:
            print(f"❌ Erro ao inicializar agente: {str(e)}")
    return _agent
