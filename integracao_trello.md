# Integração Direta com Trello no Arcee CLI

Este documento detalha as alterações feitas para integrar o Arcee CLI diretamente com a API do Trello, eliminando a dependência do servidor MCP-Trello que estava tendo problemas de timeout.

## Visão Geral da Solução

A abordagem implementada substitui:
1. As chamadas intermediárias para o servidor MCP
2. Por chamadas diretas para a API do Trello usando requisições HTTP

## Modificações Realizadas

### 1. Criação de Quadros

#### 1.1 Adição do comando `criar-quadro` no CLI

Adicionamos um novo comando ao grupo `trello_app` no arquivo `__main__.py`:

```python
@trello_app.command("criar-quadro")
def criar_quadro_trello(
    nome: str = typer.Argument(..., help="Nome do novo quadro"),
    descricao: str = typer.Option(None, "--desc", "-d", help="Descrição do quadro"),
    listas_padrao: bool = typer.Option(True, "--listas-padrao/--sem-listas", help="Criar listas padrão (A Fazer, Em Andamento, Concluído)")
):
    """Cria um novo quadro no Trello"""
    # Implementação usando requests para chamar a API do Trello diretamente
```

#### 1.2 Suporte para reconhecimento em linguagem natural

Adicionamos padrões para reconhecer comandos de criação de quadros no arquivo `trello_nl_processor.py`:

```python
# Criar quadro
(r'(criar?|adicionar?|novo)\s+(um\s+)?quadro(\s+no\s+trello)?(\s+com\s+nome|\s+chamado)?', 'criar_quadro'),
```

#### 1.3 Implementação do método para processar o comando em linguagem natural

```python
def _comando_criar_quadro(self, params: Dict[str, Any]) -> str:
    """Processa o comando para criar um quadro"""
    # Implementação usando requests para chamar a API do Trello diretamente
```

### 2. Adaptação do Comando de Listar Listas

#### 2.1 Modificação do comando `listar-listas` no CLI

Atualizamos a implementação do comando no arquivo `__main__.py`:

```python
@trello_app.command("listar-listas")
def listar_listas_trello():
    """Lista todas as listas do quadro Trello"""
    # Implementação usando requests para chamar a API do Trello diretamente
```

#### 2.2 Atualização do método para processar o comando em linguagem natural

```python
def _comando_listar_listas(self, params: Optional[Dict[str, Any]] = None) -> str:
    """Processa o comando para listar listas"""
    # Implementação usando requests para chamar a API do Trello diretamente
```

#### 2.3 Suporte para especificar quadro por ID ou URL

Atualizamos o padrão de reconhecimento para permitir especificar o quadro:

```python
# Listar listas
(r'(mostrar?|exibir?|listar?|ver?)\s+(as\s+)?listas(\s+do\s+trello)?(\s+do\s+quadro)?(\s+com\s+id)?(\s+com\s+url)?', 'listar_listas'),
```

E adicionamos extração de parâmetros para obter o ID ou URL do quadro:

```python
elif tipo_comando == 'listar_listas':
    # Tenta extrair o ID ou URL do quadro
    match_quadro_id = re.search(r'(?:quadro|board)\s+(?:com\s+id|id)\s+["\']?([A-Za-z0-9]+)["\']?', texto)
    match_quadro_url = re.search(r'(?:quadro|board)\s+(?:com\s+url|url)\s+["\']?(https?://trello\.com/b/[A-Za-z0-9]+(?:/[^"\']*)?)["\']?', texto)
    
    if match_quadro_id:
        params['quadro_id'] = match_quadro_id.group(1).strip()
    elif match_quadro_url:
        url = match_quadro_url.group(1).strip()
        # Extrai o ID do quadro da URL
        match_id = re.search(r'trello\.com/b/([^/]+)', url)
        if match_id:
            params['quadro_id'] = match_id.group(1)
        params['quadro_url'] = url
```

### 3. Adaptação do Comando de Criar Cards

#### 3.1 Modificação do comando `criar-card` no CLI

Atualizamos a implementação do comando no arquivo `__main__.py`:

```python
@trello_app.command("criar-card")
def criar_card_trello(
    lista_id: str = typer.Argument(..., help="ID da lista onde o card será criado"),
    nome: str = typer.Argument(..., help="Nome do card"),
    descricao: str = typer.Option("", "--desc", "-d", help="Descrição do card"),
    data_vencimento: str = typer.Option(None, "--due", help="Data de vencimento")
):
    """Cria um novo card em uma lista do Trello"""
    # Implementação usando requests para chamar a API do Trello diretamente
```

#### 3.2 Atualização do método para processar o comando em linguagem natural

```python
def _comando_criar_card(self, params: Dict[str, Any]) -> str:
    """Processa o comando para criar um card"""
    # Implementação usando requests para chamar a API do Trello diretamente
```

### 4. Implementação da Funcionalidade de Apagar Quadros

#### 4.1 Adição do comando `apagar-quadro` no CLI

Adicionamos um novo comando ao grupo `trello_app` no arquivo `__main__.py`:

```python
@trello_app.command("apagar-quadro")
def apagar_quadro_trello(
    quadro_id_ou_url: str = typer.Argument(..., help="ID do quadro ou URL completa do Trello"),
    confirmar: bool = typer.Option(False, "--sim", "-s", help="Confirmar exclusão sem perguntar")
):
    """Apaga um quadro do Trello permanentemente (cuidado: esta ação não pode ser desfeita)"""
    # Implementação usando requests para chamar a API do Trello diretamente
```

#### 4.2 Suporte para reconhecimento em linguagem natural

Adicionamos padrões para reconhecer comandos de exclusão de quadros no arquivo `trello_nl_processor.py`:

```python
# Apagar quadro
(r'(apagar?|deletar?|excluir?|remover?)\s+(um\s+)?quadro(\s+do\s+trello)?(\s+com\s+id|\s+com\s+url)?', 'apagar_quadro'),
```

#### 4.3 Implementação dos métodos para processar o comando em linguagem natural

Adicionamos dois métodos importantes:

```python
def _comando_apagar_quadro(self, params: Dict[str, Any]) -> str:
    """Processa o comando para apagar um quadro"""
    # Implementação que verifica o quadro e pede confirmação
```

```python
def _comando_confirmar(self) -> str:
    """Processa a confirmação para apagar o quadro"""
    # Implementação da exclusão efetiva após confirmação
```

#### 4.4 Sistema de Confirmação em Duas Etapas

Implementamos um sistema de confirmação em duas etapas para garantir que o usuário não apague um quadro acidentalmente:

1. No modo CLI:
   - O sistema pede confirmação direta com o prompt `typer.confirm`
   - O usuário também pode passar a flag `--sim` para pular a confirmação

2. No modo Chat:
   - O sistema mostra informações do quadro e pede confirmação
   - O usuário precisa digitar "sim" em uma mensagem separada
   - Usamos um dicionário `self.quadros_pendentes_exclusao` para armazenar quadros pendentes de exclusão

### 5. Implementação da Funcionalidade de Listar Quadros

#### 5.1 Adição do comando `listar-quadros` no CLI

Adicionamos um novo comando ao grupo `trello_app` no arquivo `__main__.py`:

```python
@trello_app.command("listar-quadros")
def listar_quadros_trello():
    """Lista todos os quadros do usuário no Trello"""
    # Implementação usando requests para chamar a API do Trello diretamente
```

#### 5.2 Suporte para reconhecimento em linguagem natural

Adicionamos padrões para reconhecer comandos de listagem de quadros no arquivo `trello_nl_processor.py`:

```python
# Listar quadros
(r'(mostrar?|exibir?|listar?|ver?)\s+(os\s+)?(quadros|boards?)(\s+do\s+trello)?', 'listar_quadros'),
```

#### 5.3 Implementação do método para processar o comando em linguagem natural

```python
def _comando_listar_quadros(self) -> str:
    """Processa o comando para listar todos os quadros do usuário"""
    # Implementação usando requests para chamar a API do Trello diretamente para obter todos os quadros
```

## Detalhes Técnicos da Implementação

### Acesso à API do Trello 

Para todas as operações, seguimos o seguinte padrão:

1. Obter credenciais do Trello do ambiente:
   ```python
   api_key = os.getenv("TRELLO_API_KEY")
   token = os.getenv("TRELLO_TOKEN")
   ```

2. Verificar se as credenciais existem
3. Montar os parâmetros da requisição para cada operação
4. Fazer a requisição usando a biblioteca `requests`
5. Verificar o resultado e retornar mensagens apropriadas

### Principais endpoints utilizados:

- **Criar quadro**: `POST https://api.trello.com/1/boards/`
- **Listar listas**: `GET https://api.trello.com/1/boards/{board_id}/lists`
- **Criar card**: `POST https://api.trello.com/1/cards`
- **Listar cards**: `GET https://api.trello.com/1/lists/{list_id}/cards`
- **Apagar quadro**: `DELETE https://api.trello.com/1/boards/{board_id}`
- **Listar quadros**: `GET https://api.trello.com/1/members/me/boards`

## Fluxo de uso do CLI com a Nova Implementação

### Via Comando Direto:

1. **Criar um quadro**:
   ```
   python -m arcee_cli trello criar-quadro "Nome do Quadro" --desc "Descrição do quadro"
   ```

2. **Listar quadros**:
   ```
   python -m arcee_cli trello listar-quadros
   ```

3. **Listar listas**:
   ```
   python -m arcee_cli trello listar-listas
   ```
   ou especificando um quadro:
   ```
   python -m arcee_cli trello listar-listas --quadro-id BOARD_ID
   ```

4. **Criar um card**:
   ```
   python -m arcee_cli trello criar-card LISTA_ID "Nome do Card" --desc "Descrição do card"
   ```

5. **Apagar um quadro**:
   ```
   python -m arcee_cli trello apagar-quadro BOARD_ID
   ```
   ou
   ```
   python -m arcee_cli trello apagar-quadro https://trello.com/b/BOARD_ID/nome-do-quadro
   ```

### Via Chat com Linguagem Natural:

1. Iniciar o chat:
   ```
   python -m arcee_cli chat
   ```

2. Usar comandos como:
   - "criar quadro chamado Meu Projeto"
   - "mostrar quadros do Trello"
   - "mostrar listas do Trello"
   - "mostrar listas do quadro com id 67e23be62ecfda92a5107264"
   - "mostrar listas do quadro com url https://trello.com/b/67e23be62ecfda92a5107264/nome-do-quadro"
   - "criar card Tarefa Importante na lista A Fazer"
   - "apagar quadro com url https://trello.com/b/BOARD_ID/nome-do-quadro"
   - "sim" (para confirmar a exclusão)

## Benefícios da Nova Implementação

1. **Eliminação de dependências**: Não depende mais do servidor MCP-Trello
2. **Maior confiabilidade**: Evita problemas de timeout
3. **Fluxo mais direto**: Comunicação direta com a API do Trello
4. **Melhor desempenho**: Resposta mais rápida para todas as operações
5. **Operações completas**: Suporte para o ciclo de vida completo de quadros (criar, usar e apagar)
6. **Visibilidade total**: Capacidade de listar todos os quadros disponíveis na conta do usuário
7. **Flexibilidade**: Capacidade de trabalhar com múltiplos quadros, especificando-os pelo ID ou URL

## Próximos Passos Possíveis

1. Implementar comandos adicionais (mover cards, adicionar membros, etc.)
2. Melhorar a detecção de linguagem natural para suportar mais variações
3. Adicionar cache local para melhorar o desempenho de comandos frequentes
4. Implementar funcionalidades de sincronização offline 