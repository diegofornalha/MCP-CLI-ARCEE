#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerenciamento de configuração do MCP
"""

import os
import json
from typing import Dict, List, Optional, Set
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho para o arquivo de configuração
CONFIG_DIR = os.path.expanduser("~/.arcee")
CONFIG_FILE = os.path.join(CONFIG_DIR, "mcp_config.json")

# Configura o diretório se não existir
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

# Configuração padrão
DEFAULT_CONFIG = {
    "ferramentas_ativas": [],
    "ferramentas_inativas": [],
}


def carregar_configuracao() -> Dict:
    """
    Carrega a configuração do MCP do arquivo
    
    Returns:
        Dict: Configuração do MCP
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
    
    # Se não existe ou houve erro, retorna a configuração padrão
    return DEFAULT_CONFIG.copy()


def salvar_configuracao(config: Dict) -> bool:
    """
    Salva a configuração do MCP no arquivo
    
    Args:
        config: Configuração a ser salva
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar configuração: {e}")
        return False


def listar_ferramentas_disponiveis(client) -> List[str]:
    """
    Lista todas as ferramentas disponíveis no MCP
    
    Args:
        client: Cliente MCP
        
    Returns:
        List[str]: Lista de nomes das ferramentas
    """
    try:
        resultado = client.get_tools()
        if isinstance(resultado, dict) and "error" in resultado:
            logger.error(f"Erro ao listar ferramentas: {resultado['error']}")
            return []
            
        # Extrai os nomes das ferramentas do resultado
        tools = resultado.get('content', [])
        if not tools:
            return []
            
        # Verifica se há um objeto JSON nos tools
        if len(tools) > 0 and isinstance(tools[0], dict) and 'text' in tools[0]:
            try:
                tools_json = json.loads(tools[0]['text'])
                return list(tools_json.get('tools', {}).keys())
            except:
                logger.error("Erro ao processar JSON das ferramentas")
                return []
        
        return []
    except Exception as e:
        logger.error(f"Erro ao listar ferramentas: {e}")
        return []


def ativar_ferramenta(nome: str) -> bool:
    """
    Ativa uma ferramenta MCP
    
    Args:
        nome: Nome da ferramenta
        
    Returns:
        bool: True se ativou com sucesso, False caso contrário
    """
    config = carregar_configuracao()
    ferramentas_ativas = set(config.get("ferramentas_ativas", []))
    ferramentas_inativas = set(config.get("ferramentas_inativas", []))
    
    # Remove da lista de inativas e adiciona na lista de ativas
    if nome in ferramentas_inativas:
        ferramentas_inativas.remove(nome)
    
    ferramentas_ativas.add(nome)
    
    # Atualiza a configuração
    config["ferramentas_ativas"] = list(ferramentas_ativas)
    config["ferramentas_inativas"] = list(ferramentas_inativas)
    
    return salvar_configuracao(config)


def desativar_ferramenta(nome: str) -> bool:
    """
    Desativa uma ferramenta MCP
    
    Args:
        nome: Nome da ferramenta
        
    Returns:
        bool: True se desativou com sucesso, False caso contrário
    """
    config = carregar_configuracao()
    ferramentas_ativas = set(config.get("ferramentas_ativas", []))
    ferramentas_inativas = set(config.get("ferramentas_inativas", []))
    
    # Remove da lista de ativas e adiciona na lista de inativas
    if nome in ferramentas_ativas:
        ferramentas_ativas.remove(nome)
    
    ferramentas_inativas.add(nome)
    
    # Atualiza a configuração
    config["ferramentas_ativas"] = list(ferramentas_ativas)
    config["ferramentas_inativas"] = list(ferramentas_inativas)
    
    return salvar_configuracao(config)


def obter_ferramentas_ativas() -> List[str]:
    """
    Obtém a lista de ferramentas ativas
    
    Returns:
        List[str]: Lista de nomes das ferramentas ativas
    """
    config = carregar_configuracao()
    return config.get("ferramentas_ativas", [])


def obter_ferramentas_inativas() -> List[str]:
    """
    Obtém a lista de ferramentas inativas
    
    Returns:
        List[str]: Lista de nomes das ferramentas inativas
    """
    config = carregar_configuracao()
    return config.get("ferramentas_inativas", [])


def filtrar_ferramentas(todas_ferramentas: List[str]) -> Dict[str, List[str]]:
    """
    Filtra as ferramentas com base na configuração
    
    Args:
        todas_ferramentas: Lista de todas as ferramentas disponíveis
        
    Returns:
        Dict[str, List[str]]: Dicionário com listas de ferramentas ativas e inativas
    """
    config = carregar_configuracao()
    ferramentas_ativas = set(config.get("ferramentas_ativas", []))
    ferramentas_inativas = set(config.get("ferramentas_inativas", []))
    
    # Se nenhuma ferramenta foi configurada ainda, todas estão ativas por padrão
    if not ferramentas_ativas and not ferramentas_inativas:
        return {
            "ativas": todas_ferramentas,
            "inativas": []
        }
    
    # Filtra as ferramentas
    ativas = [f for f in todas_ferramentas if f in ferramentas_ativas or (f not in ferramentas_inativas and f not in ferramentas_ativas)]
    inativas = [f for f in todas_ferramentas if f in ferramentas_inativas]
    
    return {
        "ativas": ativas,
        "inativas": inativas
    } 