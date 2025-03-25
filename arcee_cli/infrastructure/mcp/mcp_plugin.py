#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin MCP para filtrar ferramentas com base na configuração
"""

import json
import logging
from typing import Dict, Any, List

from .mcp_config import filtrar_ferramentas, listar_ferramentas_disponiveis

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPToolsPlugin:
    """
    Plugin que filtra as ferramentas do MCP de acordo com a configuração
    """

    def __init__(self, client):
        """
        Inicializa o plugin com o cliente MCP
        """
        self.client = client
        self.ferramentas_disponiveis = []
        self.ferramentas_filtradas = {}
        self.atualizar_ferramentas()

    def atualizar_ferramentas(self):
        """
        Atualiza a lista de ferramentas disponíveis e filtradas
        """
        try:
            self.ferramentas_disponiveis = listar_ferramentas_disponiveis(self.client)
            self.ferramentas_filtradas = filtrar_ferramentas(self.ferramentas_disponiveis)
            logger.info(f"Ferramentas atualizadas: {len(self.ferramentas_disponiveis)} disponíveis")
        except Exception as e:
            logger.error(f"Erro ao atualizar ferramentas: {e}")

    def filtrar_resultado_get_tools(self, resultado_original):
        """
        Filtra o resultado do get_tools para remover ferramentas inativas
        
        Args:
            resultado_original: Resultado original do get_tools
            
        Returns:
            Dict: Resultado filtrado
        """
        try:
            # Atualiza as ferramentas
            self.atualizar_ferramentas()
            
            # Verifica se há erro no resultado
            if isinstance(resultado_original, dict) and "error" in resultado_original:
                return resultado_original
                
            # Extrai o conteúdo
            content = resultado_original.get('content', [])
            if not content or not isinstance(content[0], dict) or 'text' not in content[0]:
                return resultado_original
            
            try:
                # Converte o texto para objeto JSON
                tools_json = json.loads(content[0]['text'])
                
                # Obtém as ferramentas
                tools = tools_json.get('tools', {})
                
                # Filtra as ferramentas inativas
                ferramentas_inativas = set(self.ferramentas_filtradas.get('inativas', []))
                tools_filtradas = {k: v for k, v in tools.items() if k not in ferramentas_inativas}
                
                # Reconstrói o objeto JSON
                tools_json['tools'] = tools_filtradas
                
                # Substitui no resultado original
                resultado_filtrado = resultado_original.copy()
                resultado_filtrado['content'][0]['text'] = json.dumps(tools_json)
                
                return resultado_filtrado
            except:
                logger.error("Erro ao processar JSON das ferramentas")
                return resultado_original
        except Exception as e:
            logger.error(f"Erro ao filtrar resultado get_tools: {e}")
            return resultado_original

    def interceptar_ferramenta(self, ferramenta: str, metodo: str, parametros: Dict) -> bool:
        """
        Verifica se a ferramenta está ativa
        
        Args:
            ferramenta: Nome da ferramenta
            metodo: Método a ser chamado
            parametros: Parâmetros da chamada
            
        Returns:
            bool: True se a ferramenta está ativa, False caso contrário
        """
        # Atualiza as ferramentas
        self.atualizar_ferramentas()
        
        # Sempre permite chamadas para o Veyrax (gerenciamento de memória)
        if ferramenta == 'veyrax':
            return True
            
        # Verifica se a ferramenta está na lista de ferramentas inativas
        ferramentas_inativas = set(self.ferramentas_filtradas.get('inativas', []))
        return ferramenta not in ferramentas_inativas


def criar_servidor_mcp_com_plugin(arquivo_spec, porta=None):
    """
    Cria um servidor MCP com o plugin de filtragem
    
    Args:
        arquivo_spec: Arquivo de especificação para o MCP
        porta: Porta para o servidor MCP
        
    Returns:
        Processo: Processo do servidor MCP
    """
    import subprocess
    import os
    
    # Constrói o comando
    comando = ["mcp", "dev"]
    
    # Adiciona a porta se especificada
    if porta:
        os.environ["MCP_PORT"] = str(porta)
        
    # Adiciona o arquivo de especificação
    comando.append(arquivo_spec)
    
    # Inicia o processo
    processo = subprocess.Popen(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    return processo 