#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pacote de componentes de chat

Este pacote fornece componentes para gerenciar o chat,
incluindo histórico de mensagens, interface de usuário
e processamento de comandos.
"""

from src.chat.chat_history import ChatHistory
from src.chat.chat_ui import ChatUI
from src.chat.command_processor import CommandProcessor

__all__ = ['ChatHistory', 'ChatUI', 'CommandProcessor'] 