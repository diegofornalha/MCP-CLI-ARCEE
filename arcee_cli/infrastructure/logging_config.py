#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuração de logging para a CLI Arcee
"""

import os
import logging
from logging.handlers import RotatingFileHandler

# Diretório de logs
LOG_DIR = os.path.expanduser("~/.arcee/logs")
LOG_FILE = os.path.join(LOG_DIR, "arcee.log")

# Garantir que o diretório de logs existe
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

# Formatos
CONSOLE_FORMAT = "%(levelname)s: %(message)s"
FILE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def configurar_logging(nivel_console=logging.INFO, nivel_arquivo=logging.DEBUG):
    """
    Configura o logger para a aplicação.
    
    Args:
        nivel_console: Nível de logging para o console (padrão: INFO)
        nivel_arquivo: Nível de logging para o arquivo (padrão: DEBUG)
    """
    # Configurar o logger raiz
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Captura tudo, depois filtra nos handlers
    
    # Limpar handlers existentes para evitar duplicação
    logger.handlers = []
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(nivel_console)
    console_formatter = logging.Formatter(CONSOLE_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(nivel_arquivo)
    file_formatter = logging.Formatter(FILE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # Adicionar handlers ao logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Configurar loggers específicos de bibliotecas
    configurar_loggers_bibliotecas()
    
    # Registrar configuração inicial
    logger.info(f"Sistema de logging configurado. Arquivo de log: {LOG_FILE}")
    logger.debug("Logging de DEBUG ativado")
    
    return logger

def configurar_loggers_bibliotecas():
    """
    Configura loggers de bibliotecas externas para evitar poluição da saída.
    """
    # Configurar logger de HTTP do OpenAI para WARNING (oculta mensagens INFO)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("openai.http_client").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    
    # Configurar loggers de outras bibliotecas HTTP
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

def obter_logger(nome):
    """
    Obtém um logger configurado para um módulo específico.
    
    Args:
        nome: Nome do módulo/componente
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(nome)

def definir_nivel_log(nivel):
    """
    Define o nível de log para o logger raiz.
    
    Args:
        nivel: Nível de log (logging.DEBUG, logging.INFO, etc.)
    """
    logging.getLogger().setLevel(nivel)
    
    # Atualiza também o console handler para o mesmo nível
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
            handler.setLevel(nivel)
    
    # Mantém configurações específicas de bibliotecas
    configurar_loggers_bibliotecas()
            
    return True 