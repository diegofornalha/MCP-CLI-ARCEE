# Guia de Integração de Novos MCPs na CLI Arcee

Este guia descreve o processo passo a passo para adicionar uma nova integração de MCP (Multi-Cloud Provider) à CLI Arcee, similar à integração já existente com o Trello.

## Pré-requisitos

- Conhecimento básico de Python
- Familiaridade com APIs REST
- Acesso às credenciais da API que você deseja integrar
- Ambiente de desenvolvimento configurado com o projeto Arcee CLI

## Passo 1: Planejamento da Integração

Antes de começar a codificação, planeje a integração respondendo às seguintes perguntas:

1. Quais comandos/funcionalidades você precisa implementar?
2. Quais endpoints da API serão necessários?
3. Quais parâmetros serão necessários para cada comando?
4. Como será a estrutura de autenticação?

## Passo 2: Estrutura de Arquivos

Crie os seguintes arquivos na estrutura do projeto:

```
arcee_cli/
├── tools/
│   └── nome_mcp_nl_processor.py  # Processador de linguagem natural para seu MCP
├── __main__.py  # Já existe, você irá modificá-lo
└── infrastructure/
    └── providers.py  # Já existe, pode precisar de modificações
```

## Passo 3: Configuração de Variáveis de Ambiente

1. Identifique as variáveis de ambiente necessárias para autenticação com a API (tokens, chaves, etc.)
2. Adicione-as ao arquivo `.env.template` na raiz do projeto

Exemplo:
```
# Configurações para [Nome do MCP]
NOME_MCP_API_KEY=
NOME_MCP_TOKEN=
NOME_MCP_URL=
```

## Passo 4: Desenvolvimento do Processador de Linguagem Natural

Crie o arquivo `arcee_cli/tools/nome_mcp_nl_processor.py` baseado no modelo do Trello, adaptando para a sua API:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Processador de Linguagem Natural para o [Nome do MCP]

Este módulo intercepta comandos em linguagem natural relacionados ao [Nome do MCP]
durante o chat e os traduz em ações.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
import os
import requests
from datetime import datetime
from ..infrastructure.providers import ArceeProvider

# Configuração de logging
logger = logging.getLogger("nome_mcp_nl_processor")

class NomeMCPNLProcessor:
    """
    Processador de comandos em linguagem natural para o [Nome do MCP].
    
    Esta classe detecta e processa comandos em linguagem natural relacionados
    ao [Nome do MCP] durante o chat e executa as ações correspondentes.
    """
    
    def __init__(self, agent=None):
        """
        Inicializa o processador
        
        Args:
            agent: Agente para executar comandos do [Nome do MCP]
        """
        self.agent = agent
        
        # Cache para reduzir chamadas à API
        self.cache = {}
        
        # Tempo máximo de validade do cache em segundos (5 minutos por padrão)
        self.cache_ttl = 300
        
        # Defina os padrões para comandos do seu MCP
        self.comandos_padroes = [
            # Exemplos
            (r'(mostrar?|exibir?|listar?|ver?)\s+(os\s+)?(recursos|services?)', 'listar_recursos'),
            # Adicione mais padrões conforme necessário
        ]
    
    # Implemente os métodos de detecção de comandos e processamento
    def detectar_comando(self, mensagem: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Detecta comandos na mensagem do usuário"""
        # Implemente a lógica similar ao Trello
        pass
        
    def processar_comando_com_llm(self, mensagem: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Usa a LLM para detectar comandos e extrair parâmetros"""
        # Implemente usando a mesma lógica do Trello
        pass
    
    def processar_comando(self, tipo_comando: str, params: Dict[str, Any]) -> Optional[str]:
        """Processa o comando detectado"""
        # Implemente a lógica para cada tipo de comando
        pass
    
    # Adicione os métodos específicos para cada comando
    def _comando_listar_recursos(self, params: Dict[str, Any]) -> str:
        """Exemplo de método para listar recursos"""
        # Implemente a lógica específica
        pass
```

## Passo 5: Implementação dos Métodos Específicos

Para cada comando que você planeja suportar, implemente um método específico. Por exemplo:

```python
def _comando_listar_recursos(self, params: Dict[str, Any]) -> str:
    """Processa o comando para listar recursos"""
    import requests
    import os
    
    # Obtém as credenciais
    api_key = os.getenv("NOME_MCP_API_KEY")
    token = os.getenv("NOME_MCP_TOKEN")
    
    if not api_key or not token:
        return "❌ Credenciais não encontradas. Verifique as variáveis de ambiente."
        
    # Faz a requisição para a API
    try:
        response = requests.get(
            "https://api.exemplo.com/recursos",
            headers={
                "Authorization": f"Bearer {token}",
                "X-API-Key": api_key
            }
        )
        response.raise_for_status()
        
        recursos = response.json()
        
        # Formata a resposta
        if not recursos:
            return "ℹ️ Nenhum recurso encontrado."
            
        result = "📋 Seus Recursos:\n\n"
        
        for i, recurso in enumerate(recursos, 1):
            result += f"{i}. {recurso.get('name', 'N/A')}\n"
            result += f"   ID: {recurso.get('id', 'N/A')}\n"
            result += f"   Tipo: {recurso.get('type', 'N/A')}\n\n"
            
        return result.strip()
        
    except Exception as e:
        logger.exception(f"Erro ao listar recursos: {e}")
        return f"❌ Erro ao listar recursos: {str(e)}"
```

## Passo 6: Registrar Comandos na CLI

Modifique o arquivo `arcee_cli/__main__.py` para adicionar seu grupo de comandos:

1. Importe seu processador:
```python
try:
    from .tools.nome_mcp_nl_processor import NomeMCPNLProcessor
    NOME_MCP_NL_AVAILABLE = True
except ImportError:
    NOME_MCP_NL_AVAILABLE = False
```

2. Crie um grupo de comandos:
```python
nome_mcp_app = typer.Typer(help="Comandos para interagir com [Nome do MCP]")
app.add_typer(nome_mcp_app, name="nome-mcp")
```

3. Implemente os comandos da CLI:
```python
@nome_mcp_app.command("listar-recursos")
def listar_recursos_nome_mcp():
    """Lista todos os recursos disponíveis"""
    # Verifique credenciais
    api_key = os.getenv("NOME_MCP_API_KEY")
    token = os.getenv("NOME_MCP_TOKEN")
    
    if not api_key or not token:
        typer.echo("❌ Credenciais não encontradas. Verifique as variáveis de ambiente.")
        return
    
    # Implemente a lógica
    # ...
```

## Passo 7: Integração com o Chat

No arquivo `arcee_cli/__main__.py`, na função `chat()`, adicione o processamento para seu MCP:

```python
# Inicializa o processador do seu MCP, se disponível
nome_mcp_processor = None
if NOME_MCP_NL_AVAILABLE:
    nome_mcp_processor = NomeMCPNLProcessor(agent)
    logger.info("Processador de linguagem natural do [Nome do MCP] carregado")

# Na função de processamento de mensagens do chat
if NOME_MCP_NL_AVAILABLE and nome_mcp_processor:
    # Tenta processar como comando do seu MCP
    is_nome_mcp_cmd, cmd_type, cmd_params = nome_mcp_processor.processar_comando_com_llm(user_input)
    if is_nome_mcp_cmd and cmd_type is not None:
        logger.info(f"Detectado comando do [Nome do MCP] com LLM: {cmd_type}")
        nome_mcp_response = nome_mcp_processor.processar_comando(cmd_type, cmd_params)
        
        if nome_mcp_response:
            console.print(Panel(nome_mcp_response, 
                          title="[bold]Assistente[/bold]", 
                          border_style="blue"))
            continue
```

## Passo 8: Documentação

1. Crie um arquivo `integracao_nome_mcp.md` na raiz do projeto com:
   - Descrição da integração
   - Requisitos de configuração
   - Lista de comandos disponíveis
   - Exemplos de uso

2. Atualize o README principal do projeto para mencionar a nova integração

## Passo 9: Testes

Crie testes para sua integração:

1. Teste a detecção de comandos
2. Teste o processamento de comandos
3. Teste a integração com a API
4. Teste a manipulação de erros

## Passo 10: Empacotamento e Distribuição

1. Verifique se todos os arquivos necessários estão incluídos
2. Teste a instalação em um ambiente limpo
3. Atualize o arquivo `requirements.txt` com quaisquer novas dependências

## Exemplos de Comandos e Interpretações

Para ajudar a criar suas expressões regulares e processamento LLM, aqui estão alguns exemplos:

| Comando do usuário | Tipo de comando | Parâmetros |
|-------------------|----------------|------------|
| "Listar recursos" | listar_recursos | {} |
| "Criar recurso Nome do Recurso" | criar_recurso | {"nome": "Nome do Recurso"} |
| "Atualizar recurso ID123 com nome Novo Nome" | atualizar_recurso | {"id": "ID123", "nome": "Novo Nome"} |

## Dicas para Integração com LLM

Para garantir que o LLM processe corretamente seus comandos:

1. Forneça exemplos claros no prompt do sistema
2. Defina claramente os parâmetros esperados para cada comando
3. Inclua diferentes variações de comandos nos exemplos
4. Teste diferentes formulações para garantir robustez

## Solução de Problemas Comuns

1. Certifique-se de que as credenciais estão configuradas corretamente
2. Verifique os logs para erros de API
3. Teste cada endpoint da API separadamente antes de integrar
4. Implemente um bom sistema de cache para evitar exceder limites de API

## Conclusão

Seguindo este guia, você deve ser capaz de adicionar uma nova integração de MCP ao projeto Arcee CLI de forma estruturada e compatível com o restante do sistema. O uso da LLM para processamento de comandos em linguagem natural proporciona uma experiência de usuário superior e mais flexível. 