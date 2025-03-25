from datetime import datetime
from typing import List, Optional, Dict, Any
from ...domain.memory.entities import Memory
from ...domain.memory.repositories import MemoryRepository
from .mcp_client import MCPClient


class VeyraXMemoryRepository(MemoryRepository):
    """Implementação do repositório de memórias usando VeyraX MCP."""

    def __init__(self, api_key: str):
        self.client = MCPClient(api_key)

    def save(self, memory: Memory) -> bool:
        """Salva uma memória no VeyraX."""
        return self.client.save_memory(memory.content, memory.tool_name)

    def get_all(self, tool: Optional[str] = None, limit: int = 10, offset: int = 0) -> List[Memory]:
        """
        Retorna memórias do VeyraX com suporte a paginação e filtragem.

        Args:
            tool: Nome da ferramenta para filtrar (opcional)
            limit: Número máximo de memórias a retornar
            offset: Número de memórias a pular

        Returns:
            Lista de memórias
        """
        result = self.client.get_memories(tool=tool, limit=limit, offset=offset)
        if not result or "items" not in result:
            return []

        memories = []
        for item in result["items"]:
            memory = Memory(
                content=item["memory"],
                tool_name=item.get("tool", ""),
                id=item.get("id"),
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
            )
            memories.append(memory)

        return memories

    def get_by_tool(self, tool_name: str, limit: int = 10, offset: int = 0) -> List[Memory]:
        """
        Retorna memórias de uma ferramenta com suporte a paginação.

        Args:
            tool_name: Nome da ferramenta
            limit: Número máximo de memórias a retornar
            offset: Número de memórias a pular

        Returns:
            Lista de memórias
        """
        return self.get_all(tool=tool_name, limit=limit, offset=offset)

    def get_by_id(self, memory_id: str) -> Optional[Memory]:
        """
        Retorna uma memória específica pelo ID.

        Args:
            memory_id: ID da memória

        Returns:
            Memória encontrada ou None
        """
        # Como não temos um endpoint específico para buscar por ID,
        # buscamos todas e filtramos
        memories = self.get_all(limit=1000)  # Busca um número grande para tentar encontrar
        return next((m for m in memories if m.id == memory_id), None)

    def update(self, memory: Memory) -> bool:
        """
        Atualiza uma memória existente.

        Args:
            memory: Memória com as atualizações

        Returns:
            bool indicando sucesso da operação
        """
        if not memory.id:
            return False
        return self.client.update_memory(memory.id, memory.content, memory.tool_name)

    def delete(self, memory_id: str) -> bool:
        """
        Deleta uma memória.

        Args:
            memory_id: ID da memória a ser deletada

        Returns:
            bool indicando sucesso da operação
        """
        return self.client.delete_memory(memory_id)
