#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente para API do Trello via MCP.
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional, Union, cast

class TrelloClient:
    """Cliente para interagir com a API do Trello via MCP"""
    
    def __init__(self, api_key: Optional[str] = None, token: Optional[str] = None, 
                board_id: Optional[str] = None, mcp_session: Optional[str] = None):
        """
        Inicializa o cliente Trello
        
        Args:
            api_key: Chave API do Trello (opcional, padrão: variável de ambiente TRELLO_API_KEY)
            token: Token de autorização do Trello (opcional, padrão: variável de ambiente TRELLO_TOKEN)
            board_id: ID do quadro do Trello (opcional, padrão: variável de ambiente TRELLO_BOARD_ID)
            mcp_session: ID da sessão MCP (opcional, padrão: variável de ambiente MCP_SESSION_ID)
        """
        self.api_key = api_key or os.getenv("TRELLO_API_KEY") or ""
        self.token = token or os.getenv("TRELLO_TOKEN") or ""
        self.board_id = board_id or os.getenv("TRELLO_BOARD_ID") or ""
        self.mcp_session = mcp_session or os.getenv("MCP_SESSION_ID") or ""
        
        if not self.token:
            raise ValueError("Token do Trello não encontrado. Defina a variável de ambiente TRELLO_TOKEN ou forneça o token no construtor.")
            
        if not self.mcp_session:
            raise ValueError("Sessão MCP não encontrada. Defina a variável de ambiente MCP_SESSION_ID ou forneça a sessão no construtor.")
    
    def execute_mcp_command(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Executa um comando MCP
        
        Args:
            tool_name: Nome da ferramenta Trello a executar
            params: Parâmetros para a ferramenta
            
        Returns:
            Resultado da execução (pode ser lista ou dicionário)
        """
        # Adiciona o token aos parâmetros
        if "token" not in params:
            params["token"] = self.token
            
        # Converte os parâmetros para JSON
        params_json = json.dumps(params)
        
        # Comando MCP
        cmd = [
            "mcpx", "run", f"trello.{tool_name}",
            "--json", params_json,
            "--session", self.mcp_session
        ]
        
        try:
            # Executa o comando
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Analisa a saída como JSON
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"error": "Falha ao analisar resposta JSON", "raw": result.stdout}
                
        except subprocess.CalledProcessError as e:
            return {"error": f"Falha ao executar comando MCP: {e}", "stderr": e.stderr}
    
    def get_lists(self) -> List[Dict[str, Any]]:
        """
        Obtém todas as listas do quadro configurado
        
        Returns:
            Lista de listas do quadro
        """
        if not self.board_id:
            raise ValueError("ID do quadro não configurado. Defina a variável de ambiente TRELLO_BOARD_ID ou forneça o ID no construtor.")
            
        result = self.execute_mcp_command("board_get_lists", {"board_id": self.board_id})
        return result if isinstance(result, list) else []
    
    def get_cards_by_list(self, list_id: str) -> List[Dict[str, Any]]:
        """
        Obtém todos os cartões de uma lista
        
        Args:
            list_id: ID da lista
            
        Returns:
            Lista de cartões
        """
        result = self.execute_mcp_command("get_cards_by_list_id", {"listId": list_id})
        return result if isinstance(result, list) else []
    
    def add_card(self, list_id: str, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Adiciona um cartão a uma lista
        
        Args:
            list_id: ID da lista
            name: Nome do cartão
            description: Descrição do cartão (opcional)
            
        Returns:
            Dados do cartão criado
        """
        params = {
            "listId": list_id,
            "name": name
        }
        
        if description:
            params["description"] = description
            
        return cast(Dict[str, Any], self.execute_mcp_command("add_card_to_list", params))
    
    def get_my_cards(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os cartões atribuídos ao usuário atual
        
        Returns:
            Lista de cartões do usuário
        """
        result = self.execute_mcp_command("get_my_cards", {})
        return result if isinstance(result, list) else []
        
    def add_list(self, name: str) -> Dict[str, Any]:
        """
        Adiciona uma nova lista ao quadro
        
        Args:
            name: Nome da lista
            
        Returns:
            Dados da lista criada
        """
        if not self.board_id:
            raise ValueError("ID do quadro não configurado. Defina a variável de ambiente TRELLO_BOARD_ID ou forneça o ID no construtor.")
            
        return cast(Dict[str, Any], self.execute_mcp_command("add_list_to_board", {"name": name})) 