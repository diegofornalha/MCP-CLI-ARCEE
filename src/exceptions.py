#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exceções personalizadas para o MCP-CLI-ARCEE

Este módulo define uma hierarquia de exceções personalizadas
para o projeto, permitindo um tratamento de erros mais preciso
e informativo.
"""

class MpccliException(Exception):
    """
    Exceção base para todas as exceções do projeto.
    
    Todas as exceções específicas do projeto devem herdar desta classe
    para facilitar o tratamento de erros.
    """
    pass

class LLMApiError(MpccliException):
    """
    Erro na comunicação com a API do modelo de linguagem.
    
    Esta exceção é lançada quando ocorre um erro ao comunicar com 
    a API do Arcee ou outro modelo de linguagem.
    
    Attributes:
        response (dict, optional): Resposta da API que gerou o erro
    """
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)

class ConfigurationError(MpccliException):
    """
    Erro de configuração.
    
    Esta exceção é lançada quando há problemas com a configuração 
    do sistema, como variáveis de ambiente ausentes ou inválidas.
    
    Attributes:
        config_item (str, optional): Item de configuração que causou o erro
    """
    def __init__(self, message, config_item=None):
        self.config_item = config_item
        super().__init__(message)

class AirtableApiError(MpccliException):
    """
    Erro na comunicação com a API do Airtable.
    
    Esta exceção é lançada quando ocorre um erro ao comunicar com 
    a API do Airtable, como autenticação inválida ou erro na requisição.
    
    Attributes:
        response (dict, optional): Resposta da API que gerou o erro
    """
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)

class CommandProcessingError(MpccliException):
    """
    Erro no processamento de comandos especiais.
    
    Esta exceção é lançada quando ocorre um erro ao processar
    comandos especiais no texto do chat.
    
    Attributes:
        command (str, optional): Comando que causou o erro
    """
    def __init__(self, message, command=None):
        self.command = command
        super().__init__(message)

class MCPServerError(MpccliException):
    """
    Erro relacionado aos servidores MCP.
    
    Esta exceção é lançada quando ocorre um erro ao interagir com
    servidores MCP, como servidor não disponível ou comando inválido.
    
    Attributes:
        server_name (str, optional): Nome do servidor que gerou o erro
    """
    def __init__(self, message, server_name=None):
        self.server_name = server_name
        super().__init__(message)

class VeyraxApiError(MpccliException):
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

class MCPError(MpccliException):
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