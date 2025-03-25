"""
Serviço de chat
"""

from typing import List, Dict, Optional
from ...domain.interfaces.ai_provider import AIProvider
from ...domain.models.chat_message import ChatMessage


class ChatService:
    """Serviço para gerenciar interações de chat"""

    def __init__(self, provider: AIProvider):
        """Inicializa o serviço com um provider de AI"""
        self.provider = provider
        self.context: List[ChatMessage] = []
        self.max_context = 10

    def test_connection(self) -> Dict:
        """Testa a conexão com o provider"""
        status, message = self.provider.health_check()

        if not status:
            return {"success": False, "message": message}

        # Testa geração de conteúdo
        response = self.provider.generate_content("Olá, você pode me ouvir?")
        if "error" in response:
            return {
                "success": False,
                "message": f"Erro na geração de conteúdo: {response['error']}",
            }

        return {
            "success": True,
            "message": "Conexão e geração de conteúdo funcionando",
            "model": response.get("model", "desconhecido"),
            "sample_response": response.get("text", "")[:100],
        }

    def send_message(self, content: str) -> Optional[str]:
        """Envia uma mensagem e obtém a resposta"""
        # Adiciona mensagem do usuário ao contexto
        user_message = ChatMessage(role="user", content=content)
        self.context.append(user_message)

        # Obtém resposta do modelo
        messages = [msg.to_dict() for msg in self.context]
        response = self.provider.generate_chat_content(messages)

        if "error" in response:
            return None

        # Adiciona resposta ao contexto
        ai_response = response["text"]
        ai_message = ChatMessage(role="assistant", content=ai_response)
        self.context.append(ai_message)

        # Limita o contexto
        if len(self.context) > self.max_context:
            self.context = self.context[-self.max_context :]

        return ai_response
