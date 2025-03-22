# Plano de Refatoração do Projeto MCP-CLI-ARCEE

Este documento detalha o plano de refatoração para resolver os problemas identificados na análise do código do projeto MCP-CLI-ARCEE, seguindo as regras definidas em `.cursorrules`.

## Plano de Refatoração

### Visão Geral
Este documento descreve o plano para refatoração do código-fonte do projeto MCP-CLI-ARCEE, organizando as tarefas em clusters e sub-clusters para facilitar a implementação.

### Clusters

#### Cluster 1: Arquitetura e Design (Complexidade: Alta)
Foco em reestruturar a arquitetura do sistema para facilitar manutenção e extensão.

##### Sub-Cluster 1.1: Extração de Classes Básicas (Complexidade: Baixa) ✅
**Justificativa**: Classes simples com responsabilidades bem definidas e sem dependências complexas.

**Abordagem**: 
- Criar pasta `src/chat` ✅
- Implementar classes ChatHistory e ChatUI ✅
- Criar testes unitários simples para validação

**Tarefas Concluídas**:
- ✅ Criar pasta `src/chat`
- ✅ Implementar classe `ChatHistory` em `src/chat/chat_history.py`
- ✅ Implementar classe `ChatUI` em `src/chat/chat_ui.py`
- ✅ Criar arquivo `__init__.py` para exportar as classes

##### Sub-Cluster 1.2: Processamento de Comandos (Complexidade: Média) 🔄
**Justificativa**: Envolve lógica mais complexa e integração com Airtable.

**Abordagem**:
- Criar classe CommandProcessor em `src/chat/command_processor.py` ✅
- Migrar métodos relacionados a comandos do ChatArceeMCP
- Garantir que o comportamento seja idêntico ao original
- Implementar testes de unidade

**Tarefas em Andamento**:
- ✅ Criar pasta `src/exceptions` 
- ✅ Implementar hierarquia de exceções personalizadas
- ✅ Criar classe `CommandProcessor` em `src/chat/command_processor.py`
- ⏳ Atualizar ChatArceeMCP para usar a nova classe

##### Sub-Cluster 1.3: Interfaces e Adaptadores (Complexidade: Média)
**Justificativa**: Exige compreensão de injeção de dependência e flexibilidade no design de interfaces.

**Abordagem**:
- Criar interfaces abstratas em `src/interfaces/`
- Implementar adaptadores para as integrações existentes
- Criar ServiceFactory para instanciação

**Tarefas**:
- ⏳ Criar pasta `src/interfaces`
- ⏳ Implementar interfaces `LLMClient`, `MCPService` e `TaskService`
- ⏳ Criar adaptadores para implementações existentes
- ⏳ Implementar ServiceFactory

##### Sub-Cluster 1.4: Integração Final (Complexidade: Alta)
**Justificativa**: Integra todos os componentes e requer migração cuidadosa para evitar regressões.

**Abordagem**:
- Refatorar gradualmente a classe ChatArceeMCP
- Atualizar script principal para usar ServiceFactory
- Implementar testes de integração abrangentes

**Tarefas**:
- ⏳ Refatorar classe ChatArceeMCP
- ⏳ Atualizar script principal
- ⏳ Implementar testes de integração

#### Cluster 2: Robustez e Tratamento de Erros (Complexidade: Média)
Foco em melhorar a robustez e tratamento de erros do sistema.

**Tarefas**:
- ✅ Implementar hierarquia de exceções personalizadas
- ⏳ Adicionar tratamento de erros consistente
- ⏳ Melhorar logs e feedback ao usuário

#### Cluster 3: Limpeza de Código (Complexidade: Baixa) ✅
Foco em melhorar a qualidade e legibilidade do código.

**Tarefas Concluídas**:
- ✅ Remover código não utilizado
- ✅ Adicionar comentários em áreas complexas do código
- ✅ Padronizar formatação

#### Cluster 4: Testes e Documentação (Complexidade: Média)
Foco em melhorar a cobertura de testes e a documentação.

**Tarefas**:
- ⏳ Implementar testes unitários
- ⏳ Implementar testes de integração
- ⏳ Melhorar README e documentação

### Ordem Recomendada de Implementação
1. ✅ Cluster 3: Limpeza de Código
2. ✅ Sub-Cluster 1.1: Extração de Classes Básicas
3. 🔄 Sub-Cluster 1.2: Processamento de Comandos
4. ⏳ Cluster 2: Robustez e Tratamento de Erros
5. ⏳ Sub-Cluster 1.3: Interfaces e Adaptadores
6. ⏳ Sub-Cluster 1.4: Integração Final
7. ⏳ Cluster 4: Testes e Documentação

## Divisão do Cluster 1 em Sub-Clusters de Menor Complexidade

Para facilitar a implementação do Cluster 1 (Arquitetura e Design), que possui alta complexidade, dividimos em sub-clusters menores que podem ser abordados sequencialmente:

### Sub-Cluster 1.1: Extração de Classes Básicas (Complexidade: Baixa)

**Componentes:**
- [x] Extração da classe ChatHistory
- [x] Extração da classe ChatUI

**Por que a complexidade é baixa:**
- São classes com responsabilidade única e bem definida
- Não possuem dependências complexas
- Não alteram o comportamento existente do sistema
- Podem ser implementadas e testadas isoladamente

**Abordagem:**
- [x] Criar a pasta `src/chat` para organizar as novas classes
- [x] Implementar a classe ChatHistory com métodos para gerenciar mensagens
- [x] Implementar a classe ChatUI para interação com usuário
- [ ] Criar testes unitários simples para validar o comportamento básico

### Sub-Cluster 1.2: Processamento de Comandos (Complexidade: Média)

**Componentes:**
- [ ] Extração da classe CommandProcessor
- [ ] Migração da lógica de processamento de comandos

**Por que a complexidade é média:**
- Envolve lógica mais complexa de processamento de comandos
- Depende da integração com Airtable
- Usa expressões regulares e processamento de texto
- Precisa manter compatibilidade com o comportamento atual

**Abordagem:**
1. Criar a classe CommandProcessor em `src/chat/command_processor.py`
2. Migrar métodos relacionados a comandos da classe ChatArceeMCP
3. Garantir que o comportamento seja idêntico ao original
4. Usar as exceções personalizadas já implementadas
5. Implementar testes para verificar o processamento correto de comandos

### Sub-Cluster 1.3: Interfaces e Adaptadores (Complexidade: Média)

**Componentes:**
- [ ] Criação de interfaces abstratas (LLMClient, MCPService, TaskService)
- [ ] Implementação de adaptadores para serviços existentes
- [ ] Criação do ServiceFactory

**Por que a complexidade é média:**
- Requer compreensão do padrão de injeção de dependências
- Precisa definir interfaces que sejam suficientemente flexíveis
- Deve manter compatibilidade com as implementações atuais
- Precisa prever extensibilidade futura

**Abordagem:**
1. Criar interfaces abstratas em `src/interfaces/`
2. Implementar adaptadores que encapsulam as implementações existentes
3. Criar o ServiceFactory para instanciar os serviços apropriados
4. Implementar testes para verificar o funcionamento correto dos adaptadores

### Sub-Cluster 1.4: Integração Final (Complexidade: Alta)

**Componentes:**
- [ ] Refatoração da classe principal ChatArceeMCP
- [ ] Atualização do script principal para usar o novo design

**Por que a complexidade é alta:**
- Integra todos os componentes desenvolvidos nos sub-clusters anteriores
- Representa uma mudança significativa na arquitetura do sistema
- Requer cuidadosa migração para evitar regressões
- Afeta o fluxo principal de execução do aplicativo

**Abordagem:**
1. Refatorar gradualmente a classe ChatArceeMCP para usar as novas classes
2. Implementar versão refatorada mantendo a versão original como referência
3. Atualizar o script principal para usar o ServiceFactory
4. Implementar testes de integração completos
5. Validar o comportamento do sistema antes de remover código antigo

## - [ ] 1. Resolver problema SRP: Classe ChatArceeMCP com muitas responsabilidades

### - [x] Passo 1: Extrair gerenciamento de histórico
```python
class ChatHistory:
    """Gerencia o histórico de mensagens do chat"""
    
    def __init__(self, system_instruction=None):
        self.messages = []
        if system_instruction:
            self.add_message("system", system_instruction)
    
    def add_message(self, role, content):
        """Adiciona uma mensagem ao histórico"""
        self.messages.append({"role": role, "content": content})
    
    def get_messages(self):
        """Retorna uma cópia do histórico de mensagens"""
        return self.messages.copy()
    
    def clear(self, preserve_system=True):
        """Limpa o histórico, opcionalmente preservando a mensagem do sistema"""
        system_message = None
        if preserve_system and self.messages and self.messages[0]["role"] == "system":
            system_message = self.messages[0]
        
        self.messages = []
        if system_message:
            self.messages.append(system_message)
```

### - [ ] Passo 2: Extrair processamento de comandos
```python
class CommandProcessor:
    """Processa comandos especiais no chat"""
    
    def __init__(self, airtable_service):
        self.airtable_service = airtable_service
    
    def process_commands(self, text):
        """Processa todos os comandos especiais no texto"""
        processed_text = text
        processed_text = self.process_create_task_command(processed_text)
        processed_text = self.process_list_tasks_command(processed_text)
        return processed_text
    
    def process_create_task_command(self, text):
        """Processa comandos de criação de tarefas"""
        # Lógica extraída do método original process_special_commands
        # ...
        return processed_text
    
    def process_list_tasks_command(self, text):
        """Processa comandos de listagem de tarefas"""
        # Lógica extraída do método original process_special_commands
        # ...
        return processed_text
    
    def extract_task_parameters(self, match):
        """Extrai e valida parâmetros de uma tarefa a partir de um match de regex"""
        # Lógica para extrair parâmetros
        # ...
        return params
```

### - [x] Passo 3: Extrair interface de usuário
```python
class ChatUI:
    """Gerencia a interface de usuário do chat"""
    
    def __init__(self):
        self.prompt = "\n👤 Você: "
    
    def show_welcome_message(self, servers=None):
        """Exibe mensagem de boas-vindas"""
        print("\n🤖 Chat Interativo com Arcee (modo 'auto') + Integração MCP iniciado!")
        print("   Digite 'sair', 'exit' ou 'quit' para encerrar o chat.")
        print("   Digite 'limpar' ou 'clear' para limpar o histórico.")
        if servers:
            print(f"   Servidores MCP disponíveis: {', '.join(servers)}\n")
    
    def get_user_input(self):
        """Obtém entrada do usuário"""
        return input(self.prompt)
    
    def show_thinking(self):
        """Mostra indicador de processamento"""
        print("\n🔄 Processando...")
    
    def show_response(self, text):
        """Exibe resposta do assistente"""
        print(f"\n🤖 Arcee: {text}")
    
    def show_model_info(self, response_data):
        """Exibe informações sobre o modelo utilizado"""
        # Lógica extraída do método original
        # ...
    
    def show_error(self, error_message):
        """Exibe mensagem de erro"""
        print(f"\n❌ Erro: {error_message}")
    
    def show_goodbye(self):
        """Exibe mensagem de despedida"""
        print("\n👋 Encerrando chat. Até a próxima!")
```

### - [ ] Passo 4: Refatorar a classe principal
```python
class ChatArceeMCP:
    """Implementação de chat interativo com Arcee e MCP"""
    
    def __init__(self, llm_client=None, mcp_integration=None, airtable=None, ui=None):
        # Injeção de dependências
        self.client = llm_client or self._create_default_client()
        self.mcp_integration = mcp_integration or MCPIntegration()
        self.airtable = airtable or AirtableIntegration()
        self.ui = ui or ChatUI()
        self.history = ChatHistory(self._get_system_instruction())
        self.command_processor = CommandProcessor(self.airtable)
        self.available_servers = self.mcp_integration.list_available_servers()
        
    def _create_default_client(self):
        # Lógica para criar cliente padrão
        # ...
        
    def _get_system_instruction(self):
        # Define instrução do sistema
        # ...
        
    def run(self):
        """Executa o loop principal do chat"""
        try:
            self.ui.show_welcome_message(self.available_servers)
            while True:
                user_input = self.ui.get_user_input()
                
                if self._handle_special_input(user_input):
                    continue
                
                if not user_input.strip():
                    continue
                
                response = self._process_user_message(user_input)
                if response:
                    self.ui.show_response(response.get('processed_text', response['text']))
                    self.ui.show_model_info(response)
        except KeyboardInterrupt:
            self.ui.show_goodbye()
            
    def _handle_special_input(self, user_input):
        """Trata comandos especiais do usuário"""
        # Lógica para comandos como exit, clear, etc
        # ...
        
    def _process_user_message(self, message):
        """Processa mensagem do usuário e obtém resposta"""
        # Lógica simplificada para enviar mensagem e processar resposta
        # ...
```

## - [ ] 2. Resolver problema DIP: Falta injeção de dependências

### - [ ] Passo 1: Criar interfaces abstratas
```python
from abc import ABC, abstractmethod

class LLMClient(ABC):
    """Interface para clientes de modelos de linguagem"""
    
    @abstractmethod
    def generate_content_chat(self, messages):
        """Gera conteúdo a partir de mensagens de chat"""
        pass

class MCPService(ABC):
    """Interface para serviços MCP"""
    
    @abstractmethod
    def list_available_servers(self):
        """Lista servidores disponíveis"""
        pass

class TaskService(ABC):
    """Interface para serviço de tarefas"""
    
    @abstractmethod
    def create_task(self, task_name, description, deadline, status):
        """Cria uma nova tarefa"""
        pass
    
    @abstractmethod
    def list_tasks(self):
        """Lista as tarefas existentes"""
        pass
```

### - [ ] Passo 2: Adaptar implementações existentes

```python
class ArceeClientAdapter(LLMClient):
    """Adaptador para o cliente Arcee"""
    
    def __init__(self, model="auto"):
        self.client = ArceeClient(model=model)
    
    def generate_content_chat(self, messages):
        return self.client.generate_content_chat(messages)

class MCPIntegrationAdapter(MCPService):
    """Adaptador para a integração MCP"""
    
    def __init__(self):
        self.integration = MCPIntegration()
    
    def list_available_servers(self):
        return self.integration.list_available_servers()

class AirtableServiceAdapter(TaskService):
    """Adaptador para o serviço Airtable"""
    
    def __init__(self, api_key=None, base_id=None, table_id=None):
        self.service = AirtableIntegration()
        if api_key:
            self.service.api_key = api_key
        if base_id:
            self.service.base_id = base_id
        if table_id:
            self.service.table_id = table_id
    
    def create_task(self, task_name, description=None, deadline=None, status="Not started"):
        return self.service.create_task(task_name, description, deadline, status)
    
    def list_tasks(self):
        return self.service.list_tasks()
```

### - [ ] Passo 3: Implementar Factory para criação de serviços

```python
class ServiceFactory:
    """Fábrica para criar instâncias de serviços"""
    
    @staticmethod
    def create_llm_client(client_type="arcee", **kwargs):
        """Cria cliente LLM baseado no tipo"""
        if client_type.lower() == "arcee":
            return ArceeClientAdapter(**kwargs)
        # Pode ser expandido para suportar outros tipos de cliente
        raise ValueError(f"Tipo de cliente LLM não suportado: {client_type}")
    
    @staticmethod
    def create_mcp_service():
        """Cria serviço MCP"""
        return MCPIntegrationAdapter()
    
    @staticmethod
    def create_task_service(service_type="airtable", **kwargs):
        """Cria serviço de tarefas baseado no tipo"""
        if service_type.lower() == "airtable":
            return AirtableServiceAdapter(**kwargs)
        # Pode ser expandido para suportar outros tipos de serviços
        raise ValueError(f"Tipo de serviço de tarefas não suportado: {service_type}")
```

### - [ ] Passo 4: Atualizar script principal para usar Factory

```python
def main():
    """Função principal do script"""
    try:
        # Criar serviços usando Factory
        llm_client = ServiceFactory.create_llm_client(model="auto")
        mcp_service = ServiceFactory.create_mcp_service()
        task_service = ServiceFactory.create_task_service()
        
        # Criar UI
        ui = ChatUI()
        
        # Criar e executar chat
        chat = ChatArceeMCP(llm_client, mcp_service, task_service, ui)
        chat.run()
    
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        sys.exit(1)
```

## - [x] 3. Resolver problem de funções complexas e tratamento de erros

### - [x] Passo 1: Criar exceções específicas

```python
class MpccliException(Exception):
    """Exceção base para todas as exceções do projeto"""
    pass

class LLMApiError(MpccliException):
    """Erro na comunicação com API do modelo de linguagem"""
    pass

class ConfigurationError(MpccliException):
    """Erro de configuração"""
    pass

class AirtableApiError(MpccliException):
    """Erro na comunicação com API do Airtable"""
    pass

class CommandProcessingError(MpccliException):
    """Erro no processamento de comandos"""
    pass
```

### - [x] Passo 2: Implementar tratamento de erros específico

```python
def send_message(self, message):
    """Envia uma mensagem para o modelo e retorna a resposta"""
    # Adiciona a mensagem do usuário ao histórico
    self.history.add_message("user", message)
    
    try:
        # Cria uma cópia do histórico para enviar ao modelo
        messages = self.history.get_messages()
        
        # Envia a mensagem para o modelo
        response = self.client.generate_content_chat(messages)
        
        # Verifica se houve erro
        if "error" in response and response["error"]:
            raise LLMApiError(response["error"])
        
        # Processa comandos especiais
        try:
            processed_text = self.command_processor.process_commands(response["text"])
        except CommandProcessingError as e:
            self.ui.show_error(f"Erro no processamento de comandos: {e}")
            processed_text = response["text"]
        
        # Atualiza o texto processado
        response["processed_text"] = processed_text
        
        # Adiciona a resposta ao histórico (usando o texto original para manter a consistência)
        self.history.add_message("assistant", response["text"])
        
        # Retorna a resposta
        return response
    
    except LLMApiError as e:
        self.ui.show_error(f"Erro na API do modelo: {e}")
    except AirtableApiError as e:
        self.ui.show_error(f"Erro na API do Airtable: {e}")
    except requests.RequestException as e:
        self.ui.show_error(f"Erro de comunicação com API: {e}")
    except json.JSONDecodeError as e:
        self.ui.show_error(f"Erro ao processar resposta JSON: {e}")
    except Exception as e:
        self.ui.show_error(f"Erro inesperado: {e}")
        # Log detalhado para erros inesperados
        import traceback
        traceback.print_exc()
    
    return None
```

## - [x] 4. Resolver problema YAGNI: Remover código não utilizado

### - [x] Passo 1: Remover métodos não utilizados
- Removido método `get_server_tools()` da classe `MCPIntegration` que não era usado
- Documentado mas mantido método `start_server()` por possível uso futuro

### - [x] Passo 2: Simplificar código repetitivo ou desnecessário
- Removido prompt de seleção do modelo no `teste_arcee.py`, utilizando modo "auto" por padrão 

### - [x] Passo 3: Adicionar comentários em áreas complexas
- Adicionado comentários explicativos em código complexo de processamento de comandos

### - [ ] Passo 4: Adicionar testes automatizados

Criar testes unitários e de integração para garantir que todo o código é usado e funciona corretamente:

```python
# Exemplo de estrutura de testes
import unittest
from unittest.mock import MagicMock, patch

class TestChatHistory(unittest.TestCase):
    def test_add_message(self):
        # ...
    
    def test_clear_with_preserve(self):
        # ...

class TestCommandProcessor(unittest.TestCase):
    def test_process_create_task(self):
        # ...
    
    def test_process_list_tasks(self):
        # ...

# etc.
```

## - [ ] 5. Plano de implementação

1. - [ ] **Fase 1: Refatoração estrutural**
   - [x] Criar novas classes (ChatHistory, ChatUI)
   - [ ] Implementar classe CommandProcessor
   - [ ] Refatorar ChatArceeMCP para usar essas classes
   - [ ] Implementar interfaces e adapters
   - [ ] Implementar ServiceFactory

2. - [x] **Fase 2: Melhorias de robustez**
   - [x] Implementar exceções personalizadas
   - [x] Refinar tratamento de erros
   - [ ] Adicionar logging detalhado

3. - [x] **Fase 3: Limpeza e documentação**
   - [x] Remover código não utilizado
   - [x] Adicionar comentários explicativos em áreas complexas
   - [ ] Atualizar documentação

4. - [ ] **Fase 4: Testes e validação**
   - [ ] Desenvolver testes unitários
   - [ ] Desenvolver testes de integração
   - [ ] Validar funcionalidades em ambiente real

5. - [ ] **Fase 5: Revisão final**
   - [ ] Revisar aderência às regras do `.cursorrules`
   - [ ] Validar performance
   - [ ] Incorporar feedback de usuários 