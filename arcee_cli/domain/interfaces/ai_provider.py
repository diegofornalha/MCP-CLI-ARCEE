"""
Interface base para providers de AI
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

class AIProvider(ABC):
    """Interface base para providers de AI"""
    
    @abstractmethod
    def health_check(self) -> Tuple[bool, str]:
        """Verifica a saúde do serviço"""
        pass
    
    @abstractmethod
    def generate_content(self, prompt: str) -> Dict:
        """Gera conteúdo a partir de um prompt"""
        pass
    
    @abstractmethod
    def generate_chat_content(self, messages: List[Dict[str, str]]) -> Dict:
        """Gera conteúdo em formato de chat"""
        pass 