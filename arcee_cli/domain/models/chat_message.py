"""
Modelo de mensagem de chat
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class ChatMessage:
    """Representa uma mensagem no chat"""

    role: Literal["user", "assistant"]
    content: str

    def to_dict(self) -> dict:
        """Converte a mensagem para dicionário"""
        return {"role": self.role, "content": self.content}
