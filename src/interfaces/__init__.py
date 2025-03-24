#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pacote de interfaces abstratas

Este pacote fornece interfaces abstratas para as principais 
integrações do sistema, facilitando a extensibilidade e testabilidade.
"""

from src.interfaces.llm_client import LLMClient
from src.interfaces.mcp_service import MCPService
from src.interfaces.task_service import TaskService
from src.interfaces.rest_service import RestService
from src.interfaces.file_service import FileService

__all__ = ['LLMClient', 'MCPService', 'TaskService', 'RestService', 'FileService'] 