#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Servidor MCP personalizado com suporte a ferramentas filtradas
"""

import uvicorn
import typer
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import logging
import os
from typing import Dict, Any, Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria a aplicação FastAPI
app = FastAPI(title="MCP Personalizado do Arcee")

# Armazena o cliente MCP interceptado
mcp_plugin = None


@app.get("/tools")
async def get_tools(request: Request):
    """
    Endpoint para listar ferramentas, filtrando as inativas
    """
    global mcp_plugin
    
    if not mcp_plugin:
        return JSONResponse(content={"error": "MCP não inicializado"}, status_code=500)
    
    # Obtém e filtra o resultado original
    from arcee_cli.infrastructure.mcp.cursor_client import CursorClient
    client = CursorClient()
    resultado_original = client.get_tools()
    resultado_filtrado = mcp_plugin.filtrar_resultado_get_tools(resultado_original)
    
    return JSONResponse(content=resultado_filtrado)


@app.post("/tool_call")
async def tool_call(request: Request):
    """
    Endpoint para executar ferramentas, verificando se estão ativas
    """
    global mcp_plugin
    
    if not mcp_plugin:
        return JSONResponse(content={"error": "MCP não inicializado"}, status_code=500)
    
    # Obtém os dados da requisição
    try:
        dados = await request.json()
        ferramenta = dados.get("tool")
        metodo = dados.get("method")
        parametros = dados.get("parameters", {})
        
        # Verifica se a ferramenta está ativa
        if not mcp_plugin.interceptar_ferramenta(ferramenta, metodo, parametros):
            return JSONResponse(
                content={"error": f"Ferramenta '{ferramenta}' está desativada"}, 
                status_code=403
            )
        
        # Executa a chamada original
        from arcee_cli.infrastructure.mcp.cursor_client import CursorClient
        client = CursorClient()
        resultado = client.tool_call(ferramenta, metodo, parametros)
        
        return JSONResponse(content=resultado)
    except Exception as e:
        logger.error(f"Erro ao processar chamada: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


def iniciar_servidor(host: str = "localhost", porta: int = 8083):
    """
    Inicia o servidor personalizado do MCP
    
    Args:
        host: Host para o servidor
        porta: Porta para o servidor
    """
    # Configuração para o cliente MCP
    os.environ["MCP_PORT"] = "8081"  # Porta padrão do MCP real
    
    # Inicializa o plugin
    global mcp_plugin
    from arcee_cli.infrastructure.mcp.mcp_plugin import MCPToolsPlugin
    from arcee_cli.infrastructure.mcp.cursor_client import CursorClient
    
    client = CursorClient()
    mcp_plugin = MCPToolsPlugin(client)
    
    # Inicia o servidor
    uvicorn.run(app, host=host, port=porta)


if __name__ == "__main__":
    typer.run(iniciar_servidor) 