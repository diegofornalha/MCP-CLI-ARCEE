#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Servidor MCP do Arcee usando FastAPI
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
import json
import subprocess
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import requests

# Configura logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()


@dataclass
class AppContext:
    """Contexto da aplicação"""

    api_key: str

    def to_dict(self):
        """Converte o contexto para dicionário"""
        return asdict(self)


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Gerencia o ciclo de vida da aplicação com contexto tipado"""
    # Inicializa na inicialização
    logger.debug("Iniciando ciclo de vida da aplicação")
    api_key = os.getenv("VEYRAX_API_KEY")
    if not api_key:
        # Tenta carregar da configuração do Cursor
        cursor_config = os.path.expanduser("~/.cursor/config.json")
        if os.path.exists(cursor_config):
            try:
                with open(cursor_config) as f:
                    config = json.load(f)
                    api_key = config.get("veyraxApiKey")
                    logger.debug(f"Chave API carregada do config: {api_key[:8]}...")
            except Exception as e:
                logger.error(f"Erro ao carregar config: {e}")
                pass

    if not api_key:
        logger.error("Chave API não encontrada")
        raise ValueError("Chave API não encontrada")

    try:
        context = AppContext(api_key=api_key)
        app.state.context = context.to_dict()
        logger.info("Contexto da aplicação inicializado com sucesso")
        yield
    finally:
        logger.debug("Finalizando ciclo de vida da aplicação")
        pass


# Configura o servidor FastAPI
app = FastAPI(
    title="Arcee MCP",
    description="Servidor MCP do Arcee",
    version="1.0.0",
    lifespan=app_lifespan,
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ToolCallRequest(BaseModel):
    """Modelo para requisição de chamada de ferramenta"""

    tool: str
    method: str
    parameters: Optional[Dict[str, Any]] = {}


@app.get("/tools")
async def list_tools() -> Dict[str, Any]:
    """Lista todas as ferramentas disponíveis"""
    try:
        logger.debug("Listando ferramentas disponíveis")
        return {
            "tools": [
                {
                    "name": "veyrax",
                    "description": "Integração com VeyraX",
                    "methods": {
                        "save_memory": {
                            "description": "Salva uma memória no VeyraX",
                            "parameters": {
                                "memory": {
                                    "type": "string",
                                    "description": "O conteúdo da memória",
                                },
                                "tool": {
                                    "type": "string",
                                    "description": "O nome da ferramenta associada",
                                },
                            },
                        },
                        "get_memory": {
                            "description": "Obtém memórias do VeyraX com suporte a paginação e filtragem",
                            "parameters": {
                                "tool": {
                                    "type": "string",
                                    "description": "Nome da ferramenta para filtrar (opcional)",
                                    "required": False,
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Número máximo de memórias a retornar",
                                    "default": 10,
                                    "required": False,
                                },
                                "offset": {
                                    "type": "integer",
                                    "description": "Número de memórias a pular",
                                    "default": 0,
                                    "required": False,
                                },
                            },
                        },
                        "update_memory": {
                            "description": "Atualiza uma memória existente",
                            "parameters": {
                                "id": {
                                    "type": "string",
                                    "description": "ID da memória a ser atualizada",
                                },
                                "memory": {
                                    "type": "string",
                                    "description": "Novo conteúdo da memória",
                                },
                                "tool": {
                                    "type": "string",
                                    "description": "Nome da ferramenta associada",
                                },
                            },
                        },
                        "delete_memory": {
                            "description": "Deleta uma memória",
                            "parameters": {
                                "id": {
                                    "type": "string",
                                    "description": "ID da memória a ser deletada",
                                }
                            },
                        },
                    },
                }
            ]
        }
    except Exception as e:
        logger.error(f"Erro ao listar ferramentas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool_call")
async def tool_call(request: ToolCallRequest) -> Dict[str, Any]:
    """Executa uma ferramenta específica"""
    try:
        logger.debug(f"Executando ferramenta: {request.tool}.{request.method}")
        # Obtém o contexto da aplicação
        context = app.state.context

        # Faz a requisição direta para a API do VeyraX
        veyrax_url = "https://server.smithery.ai/@VeyraX/veyrax-mcp/tool_call"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {context['api_key']}",
            "User-Agent": "Arcee-CLI/1.0",
        }

        # Monta o payload com base no método
        payload = {
            "tool": request.tool,
            "method": request.method,
            "parameters": request.parameters or {},
        }

        # Faz a requisição
        response = requests.post(veyrax_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                return {"error": error_data.get("detail", str(e))}
            except:
                return {"error": str(e)}
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta: {e}")
        return {"error": str(e)}


def run_server(host: str = "localhost", port: int = 8081):
    """Inicia o servidor com configurações personalizadas"""
    try:
        logger.info(f"Iniciando servidor em {host}:{port}")
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="debug",
            reload=False,  # Desativa reload automático
            workers=1,
            loop="auto",
            timeout_keep_alive=30,
            access_log=True,
        )
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        logger.error(f"Erro ao iniciar o servidor: {e}")
        raise


if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "localhost")
    port = int(os.getenv("MCP_PORT", "8081"))
    run_server(host, port)
