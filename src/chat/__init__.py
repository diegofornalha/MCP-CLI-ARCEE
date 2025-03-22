#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pacote de componentes de chat

Este pacote contém classes para gerenciar diferentes aspectos do chat,
como histórico de mensagens e interface de usuário.
"""

from src.chat.chat_history import ChatHistory
from src.chat.chat_ui import ChatUI

__all__ = ['ChatHistory', 'ChatUI'] 