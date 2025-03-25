from ..infrastructure.veyrax.memory_repository import VeyraXMemoryRepository
from ..application.memory.services import MemoryService


def main():
    # Configuração
    API_KEY = "vrx-f56f1108f0ab799666bbe2c87408addde6f97b22"

    # Inicialização do repositório e serviço
    repository = VeyraXMemoryRepository(API_KEY)
    service = MemoryService(repository)

    # Exemplo: Salvando uma memória
    print("Salvando memória...")
    success = service.save_memory(
        "Esta é uma memória de teste usando a nova estrutura Clean Architecture",
        "teste-clean-arch",
    )
    print(f"Memória salva: {'✅' if success else '❌'}")

    # Exemplo: Obtendo todas as memórias agrupadas
    print("\nObtendo memórias agrupadas por ferramenta:")
    memories = service.get_memories_grouped_by_tool()

    for tool, tool_memories in memories.items():
        print(f"\n📁 {tool}:")
        for memory in tool_memories:
            print(f"  - {memory}")


if __name__ == "__main__":
    main()
