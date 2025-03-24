import os
import json
import requests
from typing import Dict, List, Any, Optional, Union

from src.exceptions import VeyraxApiError

class VeyraxAdapter:
    """
    Adaptador para a API do Veyrax.
    Fornece métodos para interagir com a API do Veyrax.
    """
    
    def __init__(self, api_key: str = None, base_url: str = None, use_mock: bool = False):
        """
        Inicializa o adaptador do Veyrax.
        
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
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Obtém as ferramentas disponíveis no Veyrax.
        
        Returns:
            Lista de ferramentas disponíveis.
            
        Raises:
            VeyraxApiError: Se ocorrer um erro na API do Veyrax.
        """
        if self.use_mock:
            return self._get_mock_tools()
        
        try:
            # URL correta para obter as ferramentas conforme documentação
            response = self.session.get(f"{self.base_url}/get-tools")
            response.raise_for_status()
            
            # Processa a resposta no formato correto
            result = response.json()
            
            # Verifica se a chamada foi bem-sucedida
            if not result.get("success", False):
                error_msg = result.get("error", "Erro desconhecido")
                raise VeyraxApiError(f"Erro na API do Veyrax: {error_msg}")
            
            # Extrai os dados do formato aninhado
            if "result" in result and "data" in result["result"]:
                return result["result"]["data"].get("tools", [])
            
            # Tenta outros formatos possíveis
            if "tools" in result:
                return result["tools"]
            
            # Se não encontrar no formato esperado, retorna uma lista vazia
            return []
            
        except requests.exceptions.RequestException as e:
            raise VeyraxApiError(f"Erro ao obter ferramentas do Veyrax: {str(e)}", response=e.response)
    
    def execute_tool(self, tool_name: str, method_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ferramenta via API do Veyrax.
        
        Args:
            tool_name: Nome da ferramenta.
            method_name: Nome do método.
            parameters: Parâmetros da chamada.
            
        Returns:
            Resultado da chamada da ferramenta.
            
        Raises:
            VeyraxApiError: Se houver um erro na API.
        """
        if self.use_mock:
            return self._get_mock_tool_result(tool_name, method_name, parameters)
        
        payload = {
            "tool": tool_name,
            "method": method_name,
            "params": parameters
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/tool-call",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            # Verifica se a resposta contém uma chave 'success'
            if not result.get("success", False):
                error_msg = result.get("error", {}).get("message", "Erro desconhecido na API do Veyrax")
                raise VeyraxApiError(error_msg, result.get("error", {}))
                
            return result.get("result", {})
        except requests.RequestException as e:
            raise VeyraxApiError(f"Erro na requisição para API do Veyrax: {str(e)}")
    
    def save_memory(self, text: str) -> Dict[str, Any]:
        """
        Salva uma memória via API do Veyrax.
        
        Args:
            text: Texto da memória.
            
        Returns:
            Resultado da operação.
            
        Raises:
            VeyraxApiError: Se houver um erro na API.
        """
        params = {
            "text": text
        }
        
        return self.execute_tool("memory", "save_memory", params)
    
    def get_memories(self, filter_text: str = None, max_count: int = 100) -> Dict[str, Any]:
        """
        Recupera memórias salvas via API do Veyrax.
        
        Args:
            filter_text: Texto opcional para filtrar memórias.
            max_count: Número máximo de memórias a retornar.
            
        Returns:
            Lista de memórias.
            
        Raises:
            VeyraxApiError: Se houver um erro na API.
        """
        params = {
            "max_count": max_count
        }
        
        if filter_text:
            params["filter_text"] = filter_text
            
        return self.execute_tool("memory", "get_memories", params)
    
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Exclui uma memória do Veyrax.
        
        Args:
            memory_id: ID da memória a ser excluída.
            
        Returns:
            Resposta da API confirmando a exclusão.
            
        Raises:
            VeyraxApiError: Se ocorrer um erro na API do Veyrax.
        """
        return self.execute_tool("memory", "delete_memory", {"memory_id": memory_id})
    
    def search_memories(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Pesquisa memórias por similaridade semântica.
        
        Args:
            query: Consulta de pesquisa.
            max_results: Número máximo de resultados.
            
        Returns:
            Resultado da pesquisa.
            
        Raises:
            VeyraxApiError: Se houver um erro na API.
        """
        params = {
            "query": query,
            "max_results": max_results
        }
        
        return self.execute_tool("memory", "search_memories", params)
    
    def list_airtable_bases(self, offset: str = None) -> Dict[str, Any]:
        """
        Lista as bases disponíveis no Airtable.
        
        Args:
            offset: Token de paginação (opcional).
            
        Returns:
            Lista de bases do Airtable.
            
        Raises:
            VeyraxApiError: Se ocorrer um erro na API do Veyrax.
        """
        params = {}
        if offset:
            params["offset"] = offset
            
        return self.execute_tool("airtable", "list_bases", params)
    
    def get_base_schema(self, base_id: str, include: Any = None) -> Dict[str, Any]:
        """
        Obtém o esquema de uma base do Airtable.
        
        Args:
            base_id: ID da base do Airtable.
            include: Parâmetros adicionais de inclusão (opcional).
            
        Returns:
            Esquema da base do Airtable com suas tabelas, campos e views.
            
        Raises:
            VeyraxApiError: Se ocorrer um erro na API do Veyrax.
        """
        params = {
            "base_id": base_id
        }
        if include is not None:
            params["include"] = include
            
        return self.execute_tool("airtable", "get_base_schema", params)
    
    def list_records(
        self,
        base_id: str,
        table_id_or_name: str,
        time_zone: Optional[str] = None,
        user_locale: Optional[str] = None, 
        page_size: Optional[int] = 100,
        max_records: Optional[int] = None,
        offset: Optional[str] = None,
        view: Optional[str] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        filter_by_formula: Optional[str] = None,
        cell_format: Optional[str] = "json",
        fields: Optional[List[str]] = None,
        return_fields_by_field_id: Optional[bool] = False,
        record_metadata: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Lista registros de uma tabela do Airtable.
        
        Args:
            base_id: ID da base.
            table_id_or_name: ID ou nome da tabela.
            time_zone: Fuso horário para formatar datas/horas.
            user_locale: Localidade do usuário para formatar datas/horas.
            page_size: Número de registros por página.
            max_records: Número máximo de registros a retornar.
            offset: Token de continuação para paginação.
            view: Nome ou ID de uma visualização específica.
            sort: Lista de objetos de ordenação.
            filter_by_formula: Fórmula para filtrar registros.
            cell_format: Formato das células ('json' ou 'string').
            fields: Lista de campos a retornar.
            return_fields_by_field_id: Se retorna campos por ID ao invés de nome.
            record_metadata: Lista de metadados a incluir.
            
        Returns:
            Dicionário com os registros e token de offset se houver mais.
            
        Raises:
            VeyraxApiError: Se houver um erro na API.
        """
        parameters = {
            "base_id": base_id,
            "table_id_or_name": table_id_or_name
        }
        
        # Adiciona parâmetros opcionais apenas se não forem None
        if time_zone is not None:
            parameters["time_zone"] = time_zone
        if user_locale is not None:
            parameters["user_locale"] = user_locale
        if page_size is not None:
            parameters["page_size"] = page_size
        if max_records is not None:
            parameters["max_records"] = max_records
        if offset is not None:
            parameters["offset"] = offset
        if view is not None:
            parameters["view"] = view
        if sort is not None:
            parameters["sort"] = sort
        if filter_by_formula is not None:
            parameters["filter_by_formula"] = filter_by_formula
        if cell_format is not None:
            parameters["cell_format"] = cell_format
        if fields is not None:
            parameters["fields"] = fields
        if return_fields_by_field_id is not None:
            parameters["return_fields_by_field_id"] = return_fields_by_field_id
        if record_metadata is not None:
            parameters["record_metadata"] = record_metadata
            
        return self.execute_tool("airtable", "list_records", parameters)
    
    def _get_mock_tools(self) -> List[Dict[str, Any]]:
        """
        Retorna uma lista simulada de ferramentas disponíveis para testes.
        
        Returns:
            Lista simulada de ferramentas.
        """
        return [
            {
                "name": "memory",
                "description": "Manage memories",
                "methods": [
                    {
                        "name": "save_memory",
                        "description": "Save a memory"
                    },
                    {
                        "name": "get_memories",
                        "description": "Get memories"
                    },
                    {
                        "name": "delete_memory",
                        "description": "Delete a memory"
                    },
                    {
                        "name": "search_memories",
                        "description": "Search memories"
                    }
                ]
            },
            {
                "name": "airtable",
                "description": "Airtable integration",
                "methods": [
                    {
                        "name": "list_records",
                        "description": "List records from a table"
                    },
                    {
                        "name": "get_record",
                        "description": "Get a record by ID"
                    },
                    {
                        "name": "create_record",
                        "description": "Create a new record"
                    },
                    {
                        "name": "update_record",
                        "description": "Update an existing record"
                    },
                    {
                        "name": "delete_record",
                        "description": "Delete a record"
                    },
                    {
                        "name": "list_bases",
                        "description": "List bases"
                    },
                    {
                        "name": "get_base_schema",
                        "description": "Get base schema with tables, fields and views"
                    }
                ]
            },
            {
                "name": "email",
                "description": "Email integration",
                "methods": [
                    {
                        "name": "send_email",
                        "description": "Send an email"
                    },
                    {
                        "name": "list_emails",
                        "description": "List emails"
                    },
                    {
                        "name": "get_email",
                        "description": "Get an email by ID"
                    }
                ]
            }
        ]
    
    def _get_mock_tool_result(self, tool_name: str, method_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retorna um resultado simulado para uma chamada de ferramenta para testes.
        
        Args:
            tool_name: Nome da ferramenta.
            method_name: Nome do método.
            parameters: Parâmetros da chamada.
            
        Returns:
            Resultado simulado da chamada de ferramenta no formato da API Veyrax.
            
        Raises:
            VeyraxApiError: Se a ferramenta ou método não for suportado.
        """
        # Preparamos o payload interno primeiro
        data = {}
        
        if tool_name == "memory":
            if method_name == "save_memory":
                data = {"id": "mem_123456", "success": True}
            elif method_name == "get_memories":
                data = {
                    "memories": [
                        {"id": "mem_123456", "text": "Exemplo de memória 1", "created_at": "2023-01-01T12:00:00Z"},
                        {"id": "mem_789012", "text": "Exemplo de memória 2", "created_at": "2023-01-02T12:00:00Z"}
                    ],
                    "count": 2,
                    "total": 2
                }
            elif method_name == "delete_memory":
                data = {"success": True}
            elif method_name == "search_memories":
                data = {
                    "memories": [
                        {"id": "mem_123456", "text": "Exemplo de memória 1", "created_at": "2023-01-01T12:00:00Z"}
                    ],
                    "count": 1
                }
        
        elif tool_name == "airtable":
            if method_name == "list_records":
                # Criamos uma lista de registros de exemplo
                mock_records = [
                    {
                        "id": "rec123456",
                        "createdTime": "2023-01-01T12:00:00.000Z",
                        "fields": {
                            "Task": "Desenvolver API",
                            "Status": "Done",
                            "Notes": "API RESTful para integração com cliente",
                            "Deadline": "2023-01-15"
                        }
                    },
                    {
                        "id": "rec234567",
                        "createdTime": "2023-01-02T14:30:00.000Z",
                        "fields": {
                            "Task": "Testar integração",
                            "Status": "In progress",
                            "Notes": "Realizar testes de integração com sistema externo",
                            "Deadline": "2023-01-20"
                        }
                    },
                    {
                        "id": "rec345678",
                        "createdTime": "2023-01-03T09:15:00.000Z",
                        "fields": {
                            "Task": "Documentação",
                            "Status": "Not started",
                            "Notes": "",
                            "Deadline": "2023-01-30"
                        }
                    },
                    {
                        "id": "rec456789",
                        "createdTime": "2023-01-04T16:45:00.000Z",
                        "fields": {
                            "Task": "Reunião com cliente",
                            "Status": "Done",
                            "Notes": "Apresentação do progresso e coleta de feedback",
                            "Deadline": ""
                        }
                    },
                    {
                        "id": "rec567890",
                        "createdTime": "2023-01-05T11:20:00.000Z",
                        "fields": {
                            "Task": "Correção de bugs",
                            "Status": "In progress",
                            "Notes": "Corrigir bugs reportados na versão beta",
                            "Deadline": "2023-01-25"
                        }
                    }
                ]
                
                # Processa filtros, se existirem
                filter_formula = parameters.get("filter_by_formula")
                if filter_formula:
                    filtered_records = []
                    # Implementação simplificada de filtros para demonstração
                    for record in mock_records:
                        # Status = 'Done'
                        if filter_formula == "Status = 'Done'" and record["fields"].get("Status") == "Done":
                            filtered_records.append(record)
                        # Status = 'In progress'
                        elif filter_formula == "Status = 'In progress'" and record["fields"].get("Status") == "In progress":
                            filtered_records.append(record)
                        # Status = 'Not started'
                        elif filter_formula == "Status = 'Not started'" and record["fields"].get("Status") == "Not started":
                            filtered_records.append(record)
                        # NOT(Deadline = '')
                        elif filter_formula == "NOT(Deadline = '')" and record["fields"].get("Deadline", "") != "":
                            filtered_records.append(record)
                        # Deadline = ''
                        elif filter_formula == "Deadline = ''" and record["fields"].get("Deadline", "") == "":
                            filtered_records.append(record)
                        # NOT(Notes = '')
                        elif filter_formula == "NOT(Notes = '')" and record["fields"].get("Notes", "") != "":
                            filtered_records.append(record)
                        # Filtro complexo
                        elif filter_formula == "AND(NOT(Notes = ''), Status = 'In progress')":
                            if record["fields"].get("Notes", "") != "" and record["fields"].get("Status") == "In progress":
                                filtered_records.append(record)
                else:
                    filtered_records = mock_records
                
                # Limita o número de registros conforme parâmetros
                page_size = parameters.get("page_size", 100)
                max_records = parameters.get("max_records", page_size)
                limit = min(page_size, max_records if max_records else page_size)
                
                # Retorna os registros paginados
                records_to_return = filtered_records[:limit]
                
                # Define offset se houver mais registros
                offset = None
                if len(filtered_records) > limit:
                    offset = "mock_offset_token"
                
                data = {
                    "records": records_to_return,
                    "offset": offset
                }
            elif method_name == "get_record":
                data = {
                    "id": "rec123456",
                    "fields": {
                        "Task": "Desenvolver API",
                        "Status": "Done",
                        "Notes": "API RESTful para integração com cliente",
                        "Deadline": "2023-01-15"
                    },
                    "createdTime": "2023-01-01T12:00:00.000Z"
                }
            elif method_name == "create_record":
                data = {
                    "id": "rec789",
                    "fields": parameters.get("fields", {}),
                    "createdTime": "2023-01-03T12:00:00.000Z"
                }
            elif method_name == "update_record":
                data = {
                    "id": parameters.get("record_id", "rec123"),
                    "fields": parameters.get("fields", {}),
                    "createdTime": "2023-01-01T12:00:00.000Z"
                }
            elif method_name == "delete_record":
                data = {"deleted": True, "id": parameters.get("record_id", "rec123")}
            elif method_name == "list_bases":
                data = {
                    "bases": [
                        {
                            "id": "appt2CRa7k9cUASRJ",
                            "name": "airtable tarefas",
                            "permissionLevel": "create"
                        }
                    ],
                    "offset": None
                }
            elif method_name == "get_base_schema":
                base_id = parameters.get("base_id", "appt2CRa7k9cUASRJ")
                data = {
                    "tables": [
                        {
                            "id": "tblUatmXxgQnqEUDB",
                            "name": "Tasks",
                            "description": None,
                            "primaryFieldId": "fldiWhBaOBwuU5tjZ",
                            "fields": [
                                {"id": "fldiWhBaOBwuU5tjZ", "name": "Task", "type": "singleLineText", "description": None, "options": None},
                                {"id": "fldE5QTOqV9lLY9vC", "name": "Status", "type": "singleSelect", "description": None, "options": {"choices": [
                                    {"id": "selMFdAiXFYECLidh", "name": "Not started", "color": "redLight2"}, 
                                    {"id": "selJb88vObpIqYDcE", "name": "In progress", "color": "yellowLight2"}, 
                                    {"id": "sel6gafLI3nJRDsRc", "name": "Done", "color": "greenLight2"}
                                ]}},
                                {"id": "fldI70zcfP4KbJsH9", "name": "Notes", "type": "richText", "description": None, "options": None},
                                {"id": "fldB3pCdgnN2AQfnh", "name": "Deadline", "type": "date", "description": None, "options": {"dateFormat": {"name": "friendly", "format": "LL"}}}
                            ],
                            "views": [
                                {"id": "viwYjItTxwmuRzgiH", "name": "Grid view", "type": "grid", "visibleFieldIds": None}
                            ]
                        },
                        {
                            "id": "tblZe6XV42Hj4V7rs",
                            "name": "Projetos",
                            "description": "Tabela para gerenciar projetos",
                            "primaryFieldId": "fld9F6jLInc5m0PGk",
                            "fields": [
                                {"id": "fld9F6jLInc5m0PGk", "name": "Nome do Projeto", "type": "singleLineText", "description": "Nome do projeto", "options": None},
                                {"id": "fldiOSRb4rH9E0h4c", "name": "Descrição", "type": "multilineText", "description": "Descrição detalhada do projeto", "options": None}
                            ],
                            "views": [
                                {"id": "viwCO3R4PziyGmETx", "name": "Grid view", "type": "grid", "visibleFieldIds": None}
                            ]
                        }
                    ]
                }
        
        elif tool_name == "email":
            if method_name == "send_email":
                data = {"message_id": "msg_123456", "success": True}
            elif method_name == "list_emails":
                data = {
                    "emails": [
                        {"id": "email_1", "subject": "Teste 1", "from": "teste@exemplo.com", "date": "2023-01-01T12:00:00Z"},
                        {"id": "email_2", "subject": "Teste 2", "from": "teste2@exemplo.com", "date": "2023-01-02T12:00:00Z"}
                    ],
                    "count": 2,
                    "total": 2
                }
            elif method_name == "get_email":
                data = {
                    "id": "email_1",
                    "subject": "Teste 1",
                    "from": "teste@exemplo.com",
                    "to": "destino@exemplo.com",
                    "body": "Corpo do email de teste",
                    "date": "2023-01-01T12:00:00Z"
                }
        else:
            # Se a ferramenta não for reconhecida
            raise VeyraxApiError(
                f"Ferramenta não suportada no modo simulado: {tool_name}",
                tool=tool_name
            )
            
        if not data:
            # Se o método não for reconhecido
            raise VeyraxApiError(
                f"Método não suportado no modo simulado: {tool_name}.{method_name}",
                tool=tool_name,
                method=method_name
            )
        
        # Como nosso execute_tool já extrai o data, retornamos apenas o conteúdo de data
        # Simulando que já passamos pelo processamento da resposta
        return data
    
    def handle_request(self, action: str, params: dict = None):
        """
        Manipula solicitações para a API do Veyrax.
        
        Args:
            action: Ação a ser executada.
            params: Parâmetros da ação.
            
        Returns:
            Resultado da ação.
            
        Raises:
            ValueError: Se a ação for desconhecida.
        """
        params = params or {}
        
        if action == "get_tools":
            return self.get_tools()
        
        elif action == "execute_tool":
            tool_name = params.get("tool_name")
            method_name = params.get("method_name")
            parameters = params.get("parameters", {})
            
            if not tool_name or not method_name:
                raise ValueError("Ferramenta ou método não informados")
                
            return self.execute_tool(tool_name, method_name, parameters)
        
        elif action == "save_memory":
            text = params.get("text")
            if not text:
                raise ValueError("Texto da memória não informado")
            return self.save_memory(text)
        
        elif action == "get_memories":
            filter_text = params.get("filter_text")
            max_count = params.get("max_count", 100)
            return self.get_memories(filter_text, max_count)
        
        elif action == "delete_memory":
            memory_id = params.get("memory_id")
            if not memory_id:
                raise ValueError("ID da memória não informado")
            return self.delete_memory(memory_id)
        
        elif action == "search_memories":
            query = params.get("query")
            if not query:
                raise ValueError("Consulta de pesquisa não informada")
            max_results = params.get("max_results", 10)
            return self.search_memories(query, max_results)
        
        elif action == "list_airtable_bases":
            offset = params.get("offset")
            return self.list_airtable_bases(offset)
            
        elif action == "get_base_schema":
            base_id = params.get("base_id")
            if not base_id:
                raise ValueError("ID da base não informado")
            include = params.get("include")
            return self.get_base_schema(base_id, include)
        
        elif action == "list_records":
            base_id = params.get("base_id")
            if not base_id:
                raise ValueError("ID da base não informado")
            table_id_or_name = params.get("table_id_or_name")
            if not table_id_or_name:
                raise ValueError("ID ou nome da tabela não informado")
            time_zone = params.get("time_zone")
            user_locale = params.get("user_locale")
            page_size = params.get("page_size", 100)
            max_records = params.get("max_records")
            offset = params.get("offset")
            view = params.get("view")
            sort = params.get("sort")
            filter_by_formula = params.get("filter_by_formula")
            cell_format = params.get("cell_format", "json")
            fields = params.get("fields")
            return_fields_by_field_id = params.get("return_fields_by_field_id", False)
            record_metadata = params.get("record_metadata")
            return self.list_records(base_id, table_id_or_name, time_zone, user_locale, page_size, max_records, offset, view, sort, filter_by_formula, cell_format, fields, return_fields_by_field_id, record_metadata)
        
        else:
            raise ValueError(f"Ação desconhecida: {action}")

    def list_bases(self) -> Dict[str, Any]:
        """
        Lista as bases disponíveis no Airtable.
        
        Returns:
            Dicionário com a lista de bases e token de offset se houver mais.
            
        Raises:
            VeyraxApiError: Se houver um erro na API.
        """
        return self.execute_tool("airtable", "list_bases", {}) 