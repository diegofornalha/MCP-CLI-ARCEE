#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface para serviços de manipulação de arquivos

Define a interface abstrata para operações de manipulação de arquivos,
independente do sistema de armazenamento (local, nuvem, etc).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, BinaryIO, TextIO
from pathlib import Path


class FileService(ABC):
    """
    Interface para serviços de manipulação de arquivos
    
    Esta interface abstrai operações de leitura, escrita e 
    gerenciamento de arquivos, permitindo implementações específicas
    para diferentes sistemas de armazenamento.
    """
    
    @abstractmethod
    def initialize(self, base_path: Optional[str] = None, 
                  credentials: Optional[Dict[str, Any]] = None) -> None:
        """
        Inicializa o serviço de arquivos
        
        Args:
            base_path: Caminho base para operações de arquivo (opcional)
            credentials: Credenciais para acesso (para sistemas em nuvem)
            
        Raises:
            ConfigurationError: Se a inicialização falhar
        """
        pass
    
    @abstractmethod
    def read_text(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        Lê o conteúdo de um arquivo como texto
        
        Args:
            file_path: Caminho do arquivo
            encoding: Codificação do arquivo (padrão: utf-8)
            
        Returns:
            Conteúdo do arquivo como string
            
        Raises:
            FileOperationError: Se ocorrer erro na leitura
        """
        pass
    
    @abstractmethod
    def read_binary(self, file_path: str) -> bytes:
        """
        Lê o conteúdo de um arquivo como dados binários
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Conteúdo do arquivo como bytes
            
        Raises:
            FileOperationError: Se ocorrer erro na leitura
        """
        pass
    
    @abstractmethod
    def write_text(self, file_path: str, content: str, 
                  encoding: str = "utf-8", 
                  create_dirs: bool = True) -> bool:
        """
        Escreve texto em um arquivo
        
        Args:
            file_path: Caminho do arquivo
            content: Conteúdo a ser escrito
            encoding: Codificação do arquivo (padrão: utf-8)
            create_dirs: Se deve criar diretórios pai se não existirem
            
        Returns:
            True se a operação foi bem-sucedida
            
        Raises:
            FileOperationError: Se ocorrer erro na escrita
        """
        pass
    
    @abstractmethod
    def write_binary(self, file_path: str, content: bytes,
                    create_dirs: bool = True) -> bool:
        """
        Escreve dados binários em um arquivo
        
        Args:
            file_path: Caminho do arquivo
            content: Conteúdo binário a ser escrito
            create_dirs: Se deve criar diretórios pai se não existirem
            
        Returns:
            True se a operação foi bem-sucedida
            
        Raises:
            FileOperationError: Se ocorrer erro na escrita
        """
        pass
    
    @abstractmethod
    def list_files(self, directory_path: str, 
                  pattern: Optional[str] = None) -> List[str]:
        """
        Lista arquivos em um diretório
        
        Args:
            directory_path: Caminho do diretório
            pattern: Padrão para filtrar arquivos (opcional)
            
        Returns:
            Lista de nomes de arquivos
            
        Raises:
            FileOperationError: Se ocorrer erro na listagem
        """
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """
        Verifica se um arquivo existe
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se o arquivo existe
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """
        Remove um arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se a remoção foi bem-sucedida
            
        Raises:
            FileOperationError: Se ocorrer erro na remoção
        """
        pass
    
    @abstractmethod
    def create_directory(self, directory_path: str) -> bool:
        """
        Cria um diretório
        
        Args:
            directory_path: Caminho do diretório
            
        Returns:
            True se a criação foi bem-sucedida
            
        Raises:
            FileOperationError: Se ocorrer erro na criação
        """
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Verifica se o serviço foi inicializado
        
        Returns:
            bool indicando se o serviço está pronto para uso
        """
        pass 