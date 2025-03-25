#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wrapper para ferramentas MCP.run para uso com CrewAI
"""

from typing import List, Type, Optional, Dict, Any
from pydantic import BaseModel, create_model
import json
import logging

# Configuração de logging
logger = logging.getLogger("mcpx_tools")

# Verificação condicional para importação de CrewAI
try:
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
except ImportError:
    logger.warning("CrewAI não está disponível. Para usar este módulo, instale: pip install crewai")
    # Classe fictícia para permitir carregamento sem CrewAI
    class BaseTool:
        pass
    CREWAI_AVAILABLE = False

# Verificação condicional para importação de mcp_run
try:
    from mcp_run import Client
    MCPRUN_AVAILABLE = True
except ImportError:
    logger.warning("MCP-Run não está disponível. Para usar este módulo, instale: pip install mcp-run")
    # Classe fictícia para permitir carregamento sem mcp_run
    class Client:
        def __init__(self, *args, **kwargs):
            pass
    MCPRUN_AVAILABLE = False


class MCPTool(BaseTool):
    """Wrapper para ferramentas MCP.run para uso com CrewAI"""
    
    def __init__(self, name: str, description: str, args_schema=None):
        """Inicializa a ferramenta MCP.run"""
        self.name = name
        self.description = description
        self._client = None  # Será configurado após a criação
        self._tool_name = name
        super().__init__(name=name, description=description, args_schema=args_schema)

    def _run(self, text: Optional[str] = None, **kwargs) -> str:
        """Executa a ferramenta MCP.run com os argumentos fornecidos"""
        if not MCPRUN_AVAILABLE:
            return "Erro: MCP-Run não está disponível. Instale: pip install mcp-run"

        try:
            if text:
                try:
                    input_dict = json.loads(text)
                except json.JSONDecodeError:
                    input_dict = {"text": text}
            else:
                input_dict = kwargs

            # Registra a chamada da ferramenta no log
            logger.debug(f"Chamando ferramenta MCP.run: {self._tool_name} com argumentos: {input_dict}")
            
            # Chama a ferramenta MCP.run com os argumentos de entrada
            results = self._client.call(self._tool_name, input=input_dict)
            
            output = []
            for content in results.content:
                if content.type == "text":
                    output.append(content.text)
            return "\n".join(output)
        except Exception as e:
            logger.error(f"Falha na execução da ferramenta MCPX: {str(e)}")
            return f"Erro ao executar ferramenta {self._tool_name}: {str(e)}"


def get_mcprun_tools(session_id: Optional[str] = None) -> List[BaseTool]:
    """
    Cria ferramentas CrewAI a partir das ferramentas MCP.run instaladas
    
    Args:
        session_id: ID de sessão do MCP.run opcional
        
    Returns:
        Lista de ferramentas compatíveis com CrewAI
    """
    if not CREWAI_AVAILABLE or not MCPRUN_AVAILABLE:
        logger.warning("CrewAI ou MCP-Run não disponíveis. As ferramentas não serão criadas.")
        return []

    try:
        client = Client(session_id=session_id)
        crew_tools = []

        for tool_name, tool in client.tools.items():
            # Cria o modelo Pydantic a partir do schema
            args_schema = _convert_json_schema_to_pydantic(
                tool.input_schema,
                f"{tool_name}Schema"
            )

            # Cria a ferramenta CrewAI com o schema convertido
            crew_tool = MCPTool(
                name=tool_name,
                description=tool.description,
                args_schema=args_schema,
            )
            
            crew_tool._client = client
            crew_tool._tool_name = tool_name
            
            crew_tools.append(crew_tool)
            logger.debug(f"Ferramenta MCP.run registrada: {tool_name}")
        
        logger.info(f"Total de {len(crew_tools)} ferramentas MCP.run registradas")
        return crew_tools
    except Exception as e:
        logger.error(f"Erro ao carregar ferramentas MCP.run: {e}")
        return []


def _convert_json_schema_to_pydantic(schema: Dict[str, Any], model_name: str = "DynamicModel") -> Type[BaseModel]:
    """Converte um dicionário de schema JSON em um modelo Pydantic"""
    if not CREWAI_AVAILABLE:
        # Retorna um modelo vazio se CrewAI não estiver disponível
        return BaseModel
        
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    fields = {}
    for field_name, field_schema in properties.items():
        field_type = _get_field_type(field_schema)
        
        # Trata valores padrão corretamente
        default = field_schema.get("default", None)
        if field_name in required:
            # Campos obrigatórios não têm valor padrão
            fields[field_name] = (field_type, ...)
        else:
            # Campos opcionais com ou sem valor padrão
            fields[field_name] = (Optional[field_type], default)
    
    return create_model(model_name, **fields)


def _get_field_type(field_schema: Dict[str, Any]) -> Type:
    """Converte tipo de schema JSON para tipo Python"""
    schema_type = field_schema.get("type", "string")
    
    if schema_type == "array":
        items = field_schema.get("items", {})
        item_type = _get_field_type(items)
        return List[item_type]
    
    elif schema_type == "object":
        # Trata objetos aninhados criando um novo modelo
        return _convert_json_schema_to_pydantic(field_schema, "NestedModel")
    
    # Mapeamento de tipos básicos
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
    }
    return type_mapping.get(schema_type, str) 