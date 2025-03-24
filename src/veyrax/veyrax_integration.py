import requests
import os
import json
from typing import Dict, List, Any, Optional
import uuid

class VeyraxApiError(Exception):
    """Exceção específica para erros relacionados à API do Veyrax."""
    pass

class VeyraxIntegration:
    """
    Classe para integração com a API do Veyrax.
    """
    
    def __init__(self, api_key: str = None, base_url: str = None, use_mock: bool = False):
        """
        Inicializa a integração com o Veyrax.
        
        Args:
            api_key: Chave de API do Veyrax. Se não fornecida, tenta obter de variáveis de ambiente.
            base_url: URL base da API do Veyrax. Se não fornecida, tenta obter de variáveis de ambiente ou usa valor padrão.
            use_mock: Se True, usa dados simulados em vez de fazer chamadas reais à API.
        """
        self.api_key = api_key or os.environ.get("VEYRAX_API_KEY")
        if not self.api_key and not use_mock:
            raise ValueError("API key do Veyrax não fornecida e não encontrada nas variáveis de ambiente")
        
        # Obtém a URL base das variáveis de ambiente se não fornecida
        self.base_url = base_url or os.environ.get("VEYRAX_BASE_URL", "https://api.veyrax.com")
        self.use_mock = use_mock
        
        if not use_mock:
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
    
    def get_available_tools(self):
        """
        Obtém a lista de ferramentas disponíveis no Veyrax.
        
        Returns:
            Uma lista de ferramentas disponíveis.
        
        Raises:
            VeyraxApiError: Se ocorrer um erro ao obter as ferramentas.
        """
        if self.use_mock:
            return self._mock_get_tools()
        
        try:
            response = self.session.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise VeyraxApiError(f"Erro ao obter ferramentas do Veyrax: {str(e)}")
    
    def execute_tool(self, tool_name: str, method_name: str, parameters: dict = None):
        """
        Executa uma ferramenta no Veyrax.
        
        Args:
            tool_name: Nome da ferramenta a ser executada.
            method_name: Nome do método da ferramenta a ser executado.
            parameters: Parâmetros para execução da ferramenta.
            
        Returns:
            O resultado da execução da ferramenta.
            
        Raises:
            VeyraxApiError: Se ocorrer um erro ao executar a ferramenta.
        """
        if self.use_mock:
            return self._mock_execute_tool(tool_name, method_name, parameters)
        
        try:
            response = self.session.post(
                f"{self.base_url}/tools/{tool_name}/{method_name}",
                json=parameters or {}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise VeyraxApiError(f"Erro ao executar ferramenta {tool_name}.{method_name} no Veyrax: {str(e)}")
    
    def save_memory(self, memory_data: dict):
        """
        Salva uma memória no Veyrax.
        
        Args:
            memory_data: Dados da memória a ser salva.
            
        Returns:
            O resultado da operação de salvamento.
            
        Raises:
            VeyraxApiError: Se ocorrer um erro ao salvar a memória.
        """
        if self.use_mock:
            return self._mock_save_memory(memory_data)
        
        try:
            response = self.session.post(
                f"{self.base_url}/memory",
                json=memory_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise VeyraxApiError(f"Erro ao salvar memória no Veyrax: {str(e)}")
    
    def get_memories(self, query: str = None, limit: int = 10):
        """
        Obtém memórias do Veyrax.
        
        Args:
            query: Consulta para filtragem das memórias.
            limit: Número máximo de memórias a serem retornadas.
            
        Returns:
            Uma lista de memórias.
            
        Raises:
            VeyraxApiError: Se ocorrer um erro ao obter as memórias.
        """
        if self.use_mock:
            return self._mock_get_memories(query, limit)
        
        try:
            params = {}
            if query:
                params["query"] = query
            if limit:
                params["limit"] = limit
                
            response = self.session.get(
                f"{self.base_url}/memory",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise VeyraxApiError(f"Erro ao obter memórias do Veyrax: {str(e)}")
    
    def update_memory(self, memory_id: str, memory_data: dict):
        """
        Atualiza uma memória no Veyrax.
        
        Args:
            memory_id: ID da memória a ser atualizada.
            memory_data: Novos dados da memória.
            
        Returns:
            O resultado da operação de atualização.
            
        Raises:
            VeyraxApiError: Se ocorrer um erro ao atualizar a memória.
        """
        if self.use_mock:
            return self._mock_update_memory(memory_id, memory_data)
        
        try:
            response = self.session.put(
                f"{self.base_url}/memory/{memory_id}",
                json=memory_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise VeyraxApiError(f"Erro ao atualizar memória no Veyrax: {str(e)}")
    
    def delete_memory(self, memory_id: str):
        """
        Exclui uma memória do Veyrax.
        
        Args:
            memory_id: ID da memória a ser excluída.
            
        Returns:
            O resultado da operação de exclusão.
            
        Raises:
            VeyraxApiError: Se ocorrer um erro ao excluir a memória.
        """
        if self.use_mock:
            return self._mock_delete_memory(memory_id)
        
        try:
            response = self.session.delete(
                f"{self.base_url}/memory/{memory_id}"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise VeyraxApiError(f"Erro ao excluir memória do Veyrax: {str(e)}")
            
    # Métodos de simulação para testes
    
    def _mock_get_tools(self):
        """
        Simula a obtenção de ferramentas do Veyrax.
        
        Returns:
            Uma lista simulada de ferramentas disponíveis.
        """
        return {
            "tools": [
                {
                    "name": "linkedin",
                    "description": "Ferramenta para interagir com o LinkedIn",
                    "methods": [
                        {"name": "search_profiles", "description": "Busca perfis no LinkedIn"},
                        {"name": "get_profile", "description": "Obtém detalhes de um perfil"}
                    ]
                },
                {
                    "name": "airtable",
                    "description": "Ferramenta para interagir com o Airtable",
                    "methods": [
                        {"name": "list_records", "description": "Lista registros de uma tabela"},
                        {"name": "create_record", "description": "Cria um novo registro"},
                        {"name": "update_record", "description": "Atualiza um registro existente"},
                        {"name": "delete_record", "description": "Exclui um registro"}
                    ]
                },
                {
                    "name": "memory",
                    "description": "Sistema de memória do Veyrax",
                    "methods": [
                        {"name": "save", "description": "Salva uma memória"},
                        {"name": "get", "description": "Obtém memórias"},
                        {"name": "update", "description": "Atualiza uma memória"},
                        {"name": "delete", "description": "Exclui uma memória"}
                    ]
                }
            ]
        }
    
    def _mock_execute_tool(self, tool_name, method_name, parameters):
        """
        Simula a execução de uma ferramenta do Veyrax.
        
        Args:
            tool_name: Nome da ferramenta simulada.
            method_name: Nome do método simulado.
            parameters: Parâmetros para o método simulado.
            
        Returns:
            Uma resposta simulada para a execução da ferramenta.
        """
        if tool_name == "airtable":
            if method_name == "list_records":
                base_id = parameters.get("base_id", "mockbase")
                table_name = parameters.get("table_name", "tasks")
                
                return {
                    "success": True,
                    "data": [
                        {"id": "rec1", "fields": {"Nome": "Tarefa 1", "Status": "Done", "Data": "2023-05-10"}},
                        {"id": "rec2", "fields": {"Nome": "Tarefa 2", "Status": "In Progress", "Data": "2023-05-12"}},
                        {"id": "rec3", "fields": {"Nome": "Tarefa 3", "Status": "Done", "Data": "2023-05-15"}},
                    ]
                }
            
            if method_name == "delete_record":
                return {
                    "success": True,
                    "message": f"Registro {parameters.get('record_id', 'desconhecido')} excluído com sucesso"
                }
        
        return {
            "success": True,
            "message": f"Execução simulada de {tool_name}.{method_name}",
            "data": parameters
        }
    
    def _mock_save_memory(self, memory_data):
        """
        Simula o salvamento de uma memória.
        
        Args:
            memory_data: Dados da memória a ser salva.
            
        Returns:
            Uma resposta simulada para o salvamento da memória.
        """
        return {
            "success": True,
            "id": f"mem_{uuid.uuid4().hex[:8]}",
            "message": "Memória salva com sucesso"
        }
    
    def _mock_get_memories(self, query=None, limit=10):
        """
        Simula a obtenção de memórias.
        
        Args:
            query: Consulta para filtragem das memórias.
            limit: Número máximo de memórias a serem retornadas.
            
        Returns:
            Uma lista simulada de memórias.
        """
        memories = [
            {"id": "mem_12345678", "text": "Lembrar de verificar os emails", "created_at": "2023-05-10T10:00:00Z"},
            {"id": "mem_23456789", "text": "Reunião com equipe às 14h", "created_at": "2023-05-11T09:30:00Z"},
            {"id": "mem_34567890", "text": "Enviar relatório até sexta-feira", "created_at": "2023-05-12T11:15:00Z"},
        ]
        
        if query:
            memories = [m for m in memories if query.lower() in m["text"].lower()]
        
        return {
            "success": True,
            "data": memories[:limit]
        }
    
    def _mock_update_memory(self, memory_id, memory_data):
        """
        Simula a atualização de uma memória.
        
        Args:
            memory_id: ID da memória a ser atualizada.
            memory_data: Novos dados da memória.
            
        Returns:
            Uma resposta simulada para a atualização da memória.
        """
        return {
            "success": True,
            "id": memory_id,
            "message": "Memória atualizada com sucesso"
        }
    
    def _mock_delete_memory(self, memory_id):
        """
        Simula a exclusão de uma memória.
        
        Args:
            memory_id: ID da memória a ser excluída.
            
        Returns:
            Uma resposta simulada para a exclusão da memória.
        """
        return {
            "success": True,
            "message": f"Memória {memory_id} excluída com sucesso"
        } 