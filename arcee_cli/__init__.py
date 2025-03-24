"""
Arcee CLI - Interface de linha de comando para o Arcee AI
"""

from .presentation.cli import main
from .domain.interfaces.ai_provider import AIProvider
from .infrastructure.providers.arcee_provider import ArceeProvider
from .application.services.chat_service import ChatService

__version__ = "1.0.0" 