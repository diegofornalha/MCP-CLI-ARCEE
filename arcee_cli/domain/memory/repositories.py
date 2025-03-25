from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Memory


class MemoryRepository(ABC):
    """Interface para repositório de memórias."""

    @abstractmethod
    def save(self, memory: Memory) -> bool:
        """Salva uma memória no repositório."""
        pass

    @abstractmethod
    def get_all(self) -> List[Memory]:
        """Retorna todas as memórias."""
        pass

    @abstractmethod
    def get_by_tool(self, tool_name: str) -> List[Memory]:
        """Retorna todas as memórias de uma ferramenta."""
        pass

    @abstractmethod
    def get_by_id(self, memory_id: int) -> Optional[Memory]:
        """Retorna uma memória específica pelo ID."""
        pass
