# Arcee CLI

CLI do Arcee AI para interação com a plataforma.

## Instalação

```bash
pip install -e ".[dev]"
```

## Desenvolvimento

Para executar os checks de desenvolvimento:

```bash
# Formatação
python scripts/format.py

# Lint
python scripts/lint.py

# Testes
pytest
```
python3 -m pip install -e ".[dev]"
python3 -m venv venv && source venv/bin/activate

pip install -r requirements.txt

mcp dev sample_server.py

npx --yes -p @dylibso/mcpx@latest gen-session
We need to authenticate you to mcp.run.
Press [enter] to open the browser and return here after you have logged in.
Waiting for login completion...........
Login successful!
Session: mcpx/diegofornalha/ea3KRo4cV2dkNvxEFza16Wk0KndgNh59.pYn8hHAxyiGDOoC/qosJztjZ7U3/7mfzZPmflJ194zc
venvagents@AI MCP-CLI-ARCEE % 

## Utilizando o MCPX CrewAI

O Arcee CLI integra-se com o CrewAI para permitir a criação de agentes autônomos que podem utilizar as ferramentas do MCP.run. Para utilizar esta funcionalidade:

### Pré-requisitos

1. Instale o pacote CrewAI:
```bash
pip install crewai
```

2. Gere uma sessão MCP.run:
```bash
npx --yes -p @dylibso/mcpx@latest gen-session
```

### Configuração

A tripulação Arcee é configurada através de arquivos YAML localizados em `~/.arcee/config/`:

1. `agents.yaml` - Define os agentes da tripulação
2. `tasks.yaml` - Define as tarefas a serem executadas

### Exemplo de uso

```python
from arcee_cli.crew.arcee_crew import ArceeCrew

# Inicializar com ID de sessão MCP.run obtido anteriormente
session_id = "mcpx/username/token"
crew = ArceeCrew(session_id=session_id)

# Criar agentes e tarefas a partir dos arquivos de configuração
crew.create_agents()
crew.create_tasks()
crew.create_crew()

# Executar a tripulação
result = crew.run()
print(result)
```

### Personalização

Você pode personalizar os agentes e tarefas editando os arquivos YAML:

#### Exemplo de agents.yaml:
```yaml
assistente:
  role: "Assistente Virtual"
  goal: "Ajudar o usuário com suas tarefas"
  backstory: "Você é um assistente virtual inteligente que ajuda o usuário em diversas tarefas."
  has_tools: true
```

#### Exemplo de tasks.yaml:
```yaml
pesquisa:
  description: "Realizar pesquisa sobre um tópico fornecido pelo usuário"
  expected_output: "Informações detalhadas sobre o tópico pesquisado"
  agent: "assistente"
```

Para mais detalhes, consulte a documentação completa ou execute o script de demonstração:

```bash
python demo_mcpx.py
```

duas formas de interação com o Trello:
Via comandos tradicionais do CLI
Via linguagem natural no chat do sistema
Isso significa que além dos comandos como arcee trello list-cards, o usuário poderia, dentro do chat do sistema, simplesmente digitar algo como "mostre meus cards do Trello" ou "crie um novo card no Trello para esta tarefa" e o sistema interpretaria essa linguagem natural.


esse funciona pra criar board:
create_trello_board.py