#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptador para serviços de manipulação de arquivos

Implementa a interface FileService usando operações de arquivo padrão do Python.
"""

import os
import shutil
from pathlib import Path
import glob
from typing import Dict, List, Optional, Any, Union, BinaryIO, TextIO

from src.interfaces.file_service import FileService
from src.exceptions import FileOperationError, ConfigurationError


class LocalFileAdapter(FileService):
    """
    Adaptador para manipulação de arquivos locais
    
    Esta implementação da interface FileService utiliza as funções
    padrão do Python para manipulação de arquivos no sistema local.
    """
    
    def __init__(self):
        """Inicializa o adaptador com valores padrão"""
        self.base_path = None
        self._initialized = False
    
    def initialize(self, base_path: Optional[str] = None, 
                  credentials: Optional[Dict[str, Any]] = None) -> None:
        """
        Inicializa o serviço de arquivos
        
        Args:
            base_path: Caminho base para operações de arquivo (opcional)
            credentials: Credenciais para acesso (não usado nesta implementação)
            
        Raises:
            ConfigurationError: Se a inicialização falhar
        """
        # Se base_path não for especificado, usa o diretório atual
        if not base_path:
            base_path = os.getcwd()
        
        # Verifica se o caminho existe
        if not os.path.exists(base_path):
            try:
                os.makedirs(base_path)
            except Exception as e:
                raise ConfigurationError(f"Não foi possível criar o diretório base: {str(e)}")
        
        # Verifica se o caminho é um diretório
        if not os.path.isdir(base_path):
            raise ConfigurationError(f"O caminho especificado não é um diretório: {base_path}")
        
        # Resolve o caminho para formato absoluto
        self.base_path = os.path.abspath(base_path)
        self._initialized = True
    
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
        self._check_initialized()
        
        full_path = self._get_full_path(file_path)
        self._check_path_exists(full_path)
        
        try:
            with open(full_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            raise FileOperationError(
                f"Erro ao ler arquivo como texto: {str(e)}", 
                file_path=file_path, 
                operation="read_text"
            )
    
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
        self._check_initialized()
        
        full_path = self._get_full_path(file_path)
        self._check_path_exists(full_path)
        
        try:
            with open(full_path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise FileOperationError(
                f"Erro ao ler arquivo como binário: {str(e)}", 
                file_path=file_path, 
                operation="read_binary"
            )
    
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
        self._check_initialized()
        
        full_path = self._get_full_path(file_path)
        
        if create_dirs:
            self._ensure_directory_exists(os.path.dirname(full_path))
        
        try:
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            raise FileOperationError(
                f"Erro ao escrever em arquivo como texto: {str(e)}", 
                file_path=file_path, 
                operation="write_text"
            )
    
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
        self._check_initialized()
        
        full_path = self._get_full_path(file_path)
        
        if create_dirs:
            self._ensure_directory_exists(os.path.dirname(full_path))
        
        try:
            with open(full_path, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            raise FileOperationError(
                f"Erro ao escrever em arquivo como binário: {str(e)}", 
                file_path=file_path, 
                operation="write_binary"
            )
    
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
        self._check_initialized()
        
        full_path = self._get_full_path(directory_path)
        if not os.path.exists(full_path):
            raise FileOperationError(
                f"Diretório não encontrado: {directory_path}",
                file_path=directory_path,
                operation="list_files"
            )
        
        if not os.path.isdir(full_path):
            raise FileOperationError(
                f"O caminho especificado não é um diretório: {directory_path}",
                file_path=directory_path,
                operation="list_files"
            )
            
        try:
            if pattern:
                # Usa glob para listar arquivos com o padrão especificado
                pattern_path = os.path.join(full_path, pattern)
                files = glob.glob(pattern_path)
                # Converte para caminhos relativos ao diretório base
                return [os.path.relpath(f, self.base_path) for f in files]
            else:
                # Lista todos os arquivos no diretório
                files = [os.path.join(directory_path, f) for f in os.listdir(full_path)
                         if os.path.isfile(os.path.join(full_path, f))]
                return files
        except Exception as e:
            raise FileOperationError(
                f"Erro ao listar arquivos: {str(e)}", 
                file_path=directory_path, 
                operation="list_files"
            )
    
    def file_exists(self, file_path: str) -> bool:
        """
        Verifica se um arquivo existe
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se o arquivo existe
        """
        self._check_initialized()
        
        full_path = self._get_full_path(file_path)
        return os.path.isfile(full_path)
    
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
        self._check_initialized()
        
        full_path = self._get_full_path(file_path)
        if not os.path.exists(full_path):
            return False
        
        if not os.path.isfile(full_path):
            raise FileOperationError(
                f"O caminho especificado não é um arquivo: {file_path}",
                file_path=file_path,
                operation="delete_file"
            )
            
        try:
            os.remove(full_path)
            return True
        except Exception as e:
            raise FileOperationError(
                f"Erro ao remover arquivo: {str(e)}", 
                file_path=file_path, 
                operation="delete_file"
            )
    
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
        self._check_initialized()
        
        full_path = self._get_full_path(directory_path)
        
        if os.path.exists(full_path):
            if os.path.isdir(full_path):
                return True
            else:
                raise FileOperationError(
                    f"O caminho já existe e não é um diretório: {directory_path}",
                    file_path=directory_path,
                    operation="create_directory"
                )
                
        try:
            os.makedirs(full_path)
            return True
        except Exception as e:
            raise FileOperationError(
                f"Erro ao criar diretório: {str(e)}", 
                file_path=directory_path, 
                operation="create_directory"
            )
    
    def is_initialized(self) -> bool:
        """
        Verifica se o serviço foi inicializado
        
        Returns:
            bool indicando se o serviço está pronto para uso
        """
        return self._initialized
    
    def _get_full_path(self, relative_path: str) -> str:
        """
        Obtém o caminho completo a partir de um caminho relativo
        
        Args:
            relative_path: Caminho relativo ao diretório base
            
        Returns:
            Caminho absoluto
        """
        # Se já for um caminho absoluto, retorna sem alterações
        if os.path.isabs(relative_path):
            return relative_path
            
        return os.path.join(self.base_path, relative_path)
    
    def _check_initialized(self) -> None:
        """
        Verifica se o serviço foi inicializado, lançando exceção se não foi
        
        Raises:
            ConfigurationError: Se o serviço não foi inicializado
        """
        if not self._initialized:
            raise ConfigurationError("Serviço de arquivos não foi inicializado")
    
    def _check_path_exists(self, path: str) -> None:
        """
        Verifica se um caminho existe, lançando exceção se não existir
        
        Args:
            path: Caminho a ser verificado
            
        Raises:
            FileOperationError: Se o caminho não existir
        """
        if not os.path.exists(path):
            raise FileOperationError(
                f"Arquivo não encontrado: {path}",
                file_path=path,
                operation="check_path"
            )
    
    def _ensure_directory_exists(self, directory_path: str) -> None:
        """
        Garante que um diretório existe, criando-o se necessário
        
        Args:
            directory_path: Caminho do diretório
            
        Raises:
            FileOperationError: Se não for possível criar o diretório
        """
        if not directory_path:
            return
            
        if not os.path.exists(directory_path):
            try:
                os.makedirs(directory_path)
            except Exception as e:
                raise FileOperationError(
                    f"Não foi possível criar o diretório: {str(e)}",
                    file_path=directory_path,
                    operation="ensure_directory"
                ) 