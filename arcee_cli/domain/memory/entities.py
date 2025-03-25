from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Memory:
    """Entidade que representa uma memória no sistema."""

    content: str
    tool_name: str
    id: Optional[int] = None
    created_at: datetime = datetime.now()

    def to_dict(self) -> dict:
        """Converte a memória para dicionário."""
        return {
            "memory": self.content,
            "tool": self.tool_name,
            "id": self.id,
            "created_at": self.created_at.isoformat(),
        }
