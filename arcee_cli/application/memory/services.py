from typing import List, Optional
from ...domain.memory.entities import Memory
from ...domain.memory.repositories import MemoryRepository


class MemoryService:
    """Serviço para gerenciamento de memórias."""

    def __init__(self, repository: MemoryRepository):
        self.repository = repository

    def save_memory(self, content: str, tool_name: str) -> bool:
        """Salva uma nova memória."""
        memory = Memory(content=content, tool_name=tool_name)
        return self.repository.save(memory)

    def get_all_memories(self) -> List[Memory]:
        """Obtém todas as memórias."""
        return self.repository.get_all()

    def get_memories_by_tool(self, tool_name: str) -> List[Memory]:
        """Obtém todas as memórias de uma ferramenta."""
        return self.repository.get_by_tool(tool_name)

    def get_memory_by_id(self, memory_id: int) -> Optional[Memory]:
        """Obtém uma memória específica pelo ID."""
        return self.repository.get_by_id(memory_id)

    def get_memories_grouped_by_tool(self) -> dict:
        """Obtém todas as memórias agrupadas por ferramenta."""
        memories = self.get_all_memories()
        grouped = {}

        for memory in memories:
            tool = memory.tool_name or "general"
            if tool not in grouped:
                grouped[tool] = []
            grouped[tool].append(memory.content)

        return grouped
