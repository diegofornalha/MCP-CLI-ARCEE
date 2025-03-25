#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agente para automatizar o trabalho com a API e ferramentas
"""

import logging
from typing import Dict, List, Optional, Any

# Configuração de logging
logger = logging.getLogger("arcee_agent")

# Importação condicional da implementação simplificada de MCP
try:
    from arcee_cli.tools.mcpx_simple import MCPRunClient
    MCPRUN_AVAILABLE = True
except ImportError:
    MCPRUN_AVAILABLE = False
    logger.warning("Implementação simplificada de MCP.run não disponível")

class ArceeAgent:
    """Agente para automatizar o trabalho com a API e ferramentas"""
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Inicializa o agente
        
        Args:
            session_id: ID de sessão MCP.run opcional
        """
        self.session_id = session_id
        self.mcp_client = None
        
        # Inicializa o cliente MCP se disponível
        if MCPRUN_AVAILABLE:
            self.mcp_client = MCPRunClient(session_id=session_id)
    
    def set_session_id(self, session_id: str):
        """
        Define o ID de sessão MCP.run
        
        Args:
            session_id: ID de sessão MCP.run
        """
        self.session_id = session_id
        
        # Atualiza o cliente MCP
        if MCPRUN_AVAILABLE:
            self.mcp_client = MCPRunClient(session_id=session_id)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lista as ferramentas disponíveis no MCP.run
        
        Returns:
            Lista de ferramentas disponíveis
        """
        if not MCPRUN_AVAILABLE or not self.mcp_client:
            logger.error("Cliente MCP.run não disponível")
            return []
            
        return self.mcp_client.get_tools()
    
    def run_tool(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ferramenta MCP.run
        
        Args:
            name: Nome da ferramenta
            params: Parâmetros da ferramenta
            
        Returns:
            Resultado da execução
        """
        if not MCPRUN_AVAILABLE or not self.mcp_client:
            logger.error("Cliente MCP.run não disponível")
            return {"error": "Cliente MCP.run não disponível"}
            
        try:
            return self.mcp_client.run_tool(name, params)
        except Exception as e:
            logger.exception(f"Erro ao executar ferramenta: {e}")
            return {"error": str(e)}

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
