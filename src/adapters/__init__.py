#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptadores para interfaces abstratas

Este pacote fornece implementações concretas das interfaces
definidas no pacote interfaces, seguindo o padrão Adapter.
"""

from src.adapters.arcee_client_adapter import ArceeClientAdapter
from src.adapters.mcp_service_adapter import MCPServiceAdapter
from src.adapters.task_service_adapter import TaskServiceAdapter
from src.adapters.rest_service_adapter import RequestsRestAdapter
from src.adapters.file_service_adapter import LocalFileAdapter

__all__ = [
    'ArceeClientAdapter',
    'MCPServiceAdapter',
    'TaskServiceAdapter',
    'RequestsRestAdapter',
    'LocalFileAdapter'
] 