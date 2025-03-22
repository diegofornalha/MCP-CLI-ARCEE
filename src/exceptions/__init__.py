#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de exceções personalizadas

Este módulo define a hierarquia de exceções personalizadas para o aplicativo.
Centralizar as exceções ajuda na organização e consistência do tratamento de erros.
"""

class ArceeMCPError(Exception):
    """Exceção base para todas as exceções do aplicativo"""
    pass


class ConfigurationError(ArceeMCPError):
    """Exceção para erros de configuração, como chaves de API ausentes"""
    pass


class APIError(ArceeMCPError):
    """Exceção base para erros relacionados a chamadas de API externa"""
    pass


class LLMApiError(APIError):
    """Exceção para erros da API do LLM (Arcee ou outros)"""
    pass


class AirtableApiError(APIError):
    """Exceção para erros da API do Airtable"""
    pass


class MCPApiError(APIError):
    """Exceção para erros da API do MCP"""
    pass


class CommandProcessingError(ArceeMCPError):
    """Exceção para erros no processamento de comandos especiais"""
    
    def __init__(self, message, command=None):
        """
        Args:
            message (str): Mensagem de erro
            command (str, opcional): O comando que gerou o erro
        """
        self.command = command
        super().__init__(message)


class ChatHistoryError(ArceeMCPError):
    """Exceção para erros relacionados ao histórico de chat"""
    pass 