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


# Exceção antiga, mantida para compatibilidade
class MpccliException(ArceeMCPError):
    """Exceção base antiga, mantida para compatibilidade com código legado"""
    pass


class ConfigurationError(ArceeMCPError):
    """Exceção para erros de configuração, como chaves de API ausentes"""
    def __init__(self, message, param=None):
        self.param = param
        super().__init__(message)


class APIError(ArceeMCPError):
    """Exceção base para erros relacionados a chamadas de API externa"""
    pass


class LLMApiError(APIError):
    """Exceção para erros da API do LLM (Arcee ou outros)"""
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)


class AirtableApiError(APIError):
    """Exceção para erros da API do Airtable"""
    pass


class MCPApiError(APIError):
    """Exceção para erros da API do MCP"""
    pass


class MCPServerError(MCPApiError):
    """Exceção para erros específicos do servidor MCP"""
    
    def __init__(self, message, server=None):
        """
        Args:
            message (str): Mensagem de erro
            server (str, opcional): Nome do servidor MCP que gerou o erro
        """
        self.server = server
        super().__init__(message)


class MCPServiceError(MCPApiError):
    """Exceção para erros nos serviços MCP"""
    
    def __init__(self, message, service=None, operation=None, details=None):
        """
        Args:
            message (str): Mensagem de erro
            service (str, opcional): Nome do serviço que gerou o erro
            operation (str, opcional): Operação que falhou
            details (dict, opcional): Detalhes adicionais do erro
        """
        self.service = service
        self.operation = operation
        self.details = details
        super().__init__(message)


class TaskServiceError(APIError):
    """Exceção para erros nos serviços de tarefas"""
    
    def __init__(self, message, task_id=None):
        """
        Args:
            message (str): Mensagem de erro
            task_id (str, opcional): ID da tarefa relacionada ao erro
        """
        self.task_id = task_id
        super().__init__(message)


class RestApiError(APIError):
    """Exceção para erros em chamadas a APIs REST genéricas"""
    
    def __init__(self, message, status_code=None, response=None):
        """
        Args:
            message (str): Mensagem de erro
            status_code (int, opcional): Código de status HTTP
            response (dict, opcional): Resposta completa da API
        """
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class FileOperationError(ArceeMCPError):
    """Exceção para erros em operações de arquivo"""
    
    def __init__(self, message, file_path=None, operation=None):
        """
        Args:
            message (str): Mensagem de erro
            file_path (str, opcional): Caminho do arquivo que gerou o erro
            operation (str, opcional): Operação que falhou (read, write, etc)
        """
        self.file_path = file_path
        self.operation = operation
        super().__init__(message)


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


class VeyraxApiError(APIError):
    """
    Erro na comunicação com a API do Veyrax.
    
    Esta exceção é lançada quando ocorre um erro ao comunicar com 
    a API do Veyrax, como autenticação inválida, erro na requisição,
    ou problemas com a execução de ferramentas.
    
    Attributes:
        response (dict, optional): Resposta da API que gerou o erro
        tool (str, optional): Ferramenta que estava sendo usada quando o erro ocorreu
        method (str, optional): Método que estava sendo chamado quando o erro ocorreu
    """
    def __init__(self, message, response=None, tool=None, method=None):
        self.response = response
        self.tool = tool
        self.method = method
        super().__init__(message)


class NotImplementedError(ArceeMCPError):
    """
    Erro de funcionalidade não implementada
    
    Esta exceção é lançada quando uma funcionalidade esperada
    não está implementada na classe/método atual.
    
    Attributes:
        method (str, optional): Nome do método não implementado
    """
    def __init__(self, message, method=None):
        self.method = method
        super().__init__(message)


class MCPError(MCPApiError):
    """
    Erro relacionado a chamadas de ferramentas MCP.
    
    Esta exceção é lançada quando ocorre um erro ao executar ferramentas
    via protocolo MCP, como ferramenta não disponível ou erro na execução.
    
    Attributes:
        tool (str, optional): Ferramenta que estava sendo usada quando o erro ocorreu
        method (str, optional): Método que estava sendo chamado quando o erro ocorreu
        parameters (dict, optional): Parâmetros que estavam sendo usados quando o erro ocorreu
    """
    def __init__(self, message, tool=None, method=None, parameters=None):
        self.tool = tool
        self.method = method
        self.parameters = parameters
        super().__init__(message) 