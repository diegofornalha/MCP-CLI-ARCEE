#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Definição de agentes especializados para o Arcee CLI usando crewAI
"""

from typing import List, Optional, Dict, Any
from crewai import Agent, Task
from crewai.tools import BaseTool

from arcee_cli.infrastructure.providers.arcee_provider import ArceeProvider
from mcp_server_cursor.veyrax_mcp_server.tools import VeyraXTools


def create_tooling_agent(tools: Optional[List[BaseTool]] = None) -> Agent:
    """
    Cria um agente especializado em usar ferramentas

    Args:
        tools: Lista de ferramentas para o agente

    Returns:
        Agent: Um agente do crewAI especializado em ferramentas
    """
    veyrax_tools = VeyraXTools().get_tools()

    if tools:
        all_tools = veyrax_tools + tools
    else:
        all_tools = veyrax_tools

    return Agent(
        role="Especialista em Ferramentas",
        goal="Ajudar o usuário a encontrar e usar as ferramentas certas para resolver seus problemas",
        backstory="""
        Você é um especialista em ferramentas que conhece profundamente todas as APIs e recursos disponíveis.
        Sua especialidade é saber exatamente qual ferramenta usar para cada tarefa e como usá-la corretamente.
        Você entende como compor ferramentas complexas para resolver problemas difíceis.
        """,
        verbose=True,
        allow_delegation=True,
        tools=all_tools,
    )


def create_research_agent(tools: Optional[List[BaseTool]] = None) -> Agent:
    """
    Cria um agente especializado em pesquisa

    Args:
        tools: Lista de ferramentas para o agente

    Returns:
        Agent: Um agente do crewAI especializado em pesquisa
    """
    veyrax_tools = VeyraXTools().get_tools()

    if tools:
        all_tools = veyrax_tools + tools
    else:
        all_tools = veyrax_tools

    return Agent(
        role="Pesquisador",
        goal="Encontrar informações precisas e relevantes para responder às perguntas do usuário",
        backstory="""
        Você é um pesquisador especializado em encontrar informações precisas.
        Você sabe como buscar dados em diversas fontes, analisar resultados e sintetizar informações
        para fornecer respostas precisas às consultas. Você é meticuloso e sempre verifica suas fontes.
        """,
        verbose=True,
        allow_delegation=True,
        tools=all_tools,
    )


def create_coding_agent(tools: Optional[List[BaseTool]] = None) -> Agent:
    """
    Cria um agente especializado em programação

    Args:
        tools: Lista de ferramentas para o agente

    Returns:
        Agent: Um agente do crewAI especializado em programação
    """
    veyrax_tools = VeyraXTools().get_tools()

    if tools:
        all_tools = veyrax_tools + tools
    else:
        all_tools = veyrax_tools

    return Agent(
        role="Programador",
        goal="Escrever, analisar e corrigir código para resolver problemas técnicos",
        backstory="""
        Você é um programador experiente com conhecimento profundo em múltiplas linguagens de programação.
        Você sabe como escrever código limpo, eficiente e bem documentado.
        Você é ótimo em encontrar bugs, otimizar código e implementar novos recursos.
        """,
        verbose=True,
        allow_delegation=True,
        tools=all_tools,
    )
