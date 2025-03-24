#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Servidor MCP (Model Control Protocol) para integração com diferentes serviços
"""

import os
import json
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
VEYRAX_API_KEY = os.getenv("VEYRAX_API_KEY")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

# Criar aplicação FastAPI
app = FastAPI(
    title="MCP Server",
    description="Servidor MCP para integração com diferentes serviços",
    version="1.0.0"
)

class MCPRequest(BaseModel):
    """Modelo para requisições MCP"""
    tool: str
    method: str
    parameters: Dict[str, Any]

class ChatRequest(BaseModel):
    """Modelo para requisições de chat"""
    model: str
    messages: List[Dict[str, str]]
    max_tokens: int = 1000

@app.get("/health")
async def health_check():
    """Verifica a saúde do servidor"""
    return {"status": "healthy"}

@app.post("/api/mcp/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """Endpoint de chat compatível com o cliente Arcee"""
    try:
        # Encaminha a requisição para o VeyraX
        if not VEYRAX_API_KEY:
            raise HTTPException(status_code=500, detail="VEYRAX_API_KEY não configurada")
        
        headers = {
            "Authorization": f"Bearer {VEYRAX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        base_url = os.getenv("VEYRAX_BASE_URL", "https://api.veyrax.com")
        
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            headers=headers,
            json=request.dict(),
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mcp")
async def handle_mcp_request(request: MCPRequest):
    """Processa requisições MCP"""
    try:
        if request.tool == "veyrax":
            return await handle_veyrax_request(request.method, request.parameters)
        elif request.tool == "airtable":
            return await handle_airtable_request(request.method, request.parameters)
        else:
            raise HTTPException(status_code=400, detail=f"Ferramenta não suportada: {request.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_veyrax_request(method: str, parameters: Dict[str, Any]):
    """Processa requisições para o VeyraX"""
    if not VEYRAX_API_KEY:
        raise HTTPException(status_code=500, detail="VEYRAX_API_KEY não configurada")
    
    headers = {
        "Authorization": f"Bearer {VEYRAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    base_url = os.getenv("VEYRAX_BASE_URL", "https://api.veyrax.com")
    
    try:
        if method == "get_tools":
            response = requests.get(f"{base_url}/tools", headers=headers)
        elif method == "tool_call":
            response = requests.post(f"{base_url}/tool_call", headers=headers, json=parameters)
        else:
            raise HTTPException(status_code=400, detail=f"Método não suportado: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_airtable_request(method: str, parameters: Dict[str, Any]):
    """Processa requisições para o Airtable"""
    if not AIRTABLE_API_KEY:
        raise HTTPException(status_code=500, detail="AIRTABLE_API_KEY não configurada")
    
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    base_url = "https://api.airtable.com/v0"
    
    try:
        if method == "list_bases":
            response = requests.get(f"{base_url}/meta/bases", headers=headers)
        elif method == "list_tables":
            base_id = parameters.get("base_id")
            if not base_id:
                raise HTTPException(status_code=400, detail="base_id é obrigatório")
            response = requests.get(f"{base_url}/meta/bases/{base_id}/tables", headers=headers)
        elif method == "list_records":
            base_id = parameters.get("base_id")
            table_name = parameters.get("table_name")
            if not base_id or not table_name:
                raise HTTPException(status_code=400, detail="base_id e table_name são obrigatórios")
            response = requests.get(f"{base_url}/{base_id}/{table_name}", headers=headers)
        else:
            raise HTTPException(status_code=400, detail=f"Método não suportado: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000) 