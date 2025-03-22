#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de gerenciamento de histórico de chat

Este módulo fornece a classe ChatHistory para gerenciar o histórico
de mensagens em um chat, permitindo adicionar mensagens, obter o 
histórico e limpar as mensagens.
"""

class ChatHistory:
    """Gerencia o histórico de mensagens do chat"""
    
    def __init__(self, system_instruction=None):
        """
        Inicializa o histórico de chat

        Args:
            system_instruction (str, optional): Instrução de sistema inicial
        """
        self.messages = []
        if system_instruction:
            self.add_message("system", system_instruction)
    
    def add_message(self, role, content):
        """
        Adiciona uma mensagem ao histórico

        Args:
            role (str): Papel do emissor da mensagem (system, user, assistant)
            content (str): Conteúdo da mensagem
        """
        self.messages.append({"role": role, "content": content})
    
    def get_messages(self):
        """
        Retorna uma cópia do histórico de mensagens
        
        Returns:
            list: Cópia do histórico de mensagens
        """
        return self.messages.copy()
    
    def clear(self, preserve_system=True):
        """
        Limpa o histórico, opcionalmente preservando a mensagem do sistema
        
        Args:
            preserve_system (bool, optional): Se True, preserva a mensagem 
                                              do sistema. Padrão é True.
        """
        system_message = None
        if preserve_system and self.messages and self.messages[0]["role"] == "system":
            system_message = self.messages[0]
        
        self.messages = []
        if system_message:
            self.messages.append(system_message)
    
    def __len__(self):
        """
        Retorna o número de mensagens no histórico
        
        Returns:
            int: Número de mensagens
        """
        return len(self.messages) 