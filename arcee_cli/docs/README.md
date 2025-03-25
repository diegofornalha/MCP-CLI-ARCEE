# Arcee CLI

Interface de linha de comando para interagir com a plataforma Arcee AI.

## Funcionalidades

- **Chat**: Inicie conversas com o modelo Arcee AI
- **MCP**: Gerencie ferramentas do Model Control Protocol (MCP)
- **Logs**: Visualize e gerencie os logs do sistema

## Requisitos

- Python 3.8+
- Pacotes Python conforme requirements.txt

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/arcee-cli.git
cd arcee-cli

# Instale as dependências
pip install -r requirements.txt

# Ou instale o pacote em desenvolvimento
pip install -e .
```

## Configuração

Configure sua chave API:

```bash
arcee configure --api-key="sua-chave-api"
```

## Uso Básico

### Chat com Arcee AI

```bash
arcee chat
```

### Gerenciamento do MCP

```bash
# Iniciar o servidor MCP
arcee mcp iniciar

# Listar ferramentas disponíveis
arcee mcp listar

# Ativar uma ferramenta
arcee mcp ativar nome-da-ferramenta

# Desativar uma ferramenta
arcee mcp desativar nome-da-ferramenta

# Parar o servidor MCP
arcee mcp parar
```

### Gerenciamento de Logs

O Arcee CLI possui um sistema de logs completo para facilitar a depuração de problemas e o monitoramento do sistema. Os logs são armazenados em `~/.arcee/logs/arcee.log`.

#### Comandos de Log

```bash
# Listar arquivos de log disponíveis
arcee logs listar

# Ver o conteúdo de um arquivo de log (últimas 50 linhas por padrão)
arcee logs ver

# Ver mais linhas de um arquivo específico
arcee logs ver --linhas=100 --arquivo=arcee.log

# Limpar os arquivos de log (com confirmação)
arcee logs limpar

# Limpar sem confirmação
arcee logs limpar --sim

# Alterar o nível de log para a sessão atual
arcee logs nivel debug

# Gerar mensagens de teste em todos os níveis
arcee logs teste
```

#### Níveis de Log

- **debug**: Informações detalhadas para diagnóstico
- **info**: Confirmação de que as coisas estão funcionando como esperado
- **warning**: Indicação de que algo inesperado aconteceu
- **error**: Erros que não impediram a execução
- **critical**: Erros graves que podem impedir o funcionamento

## Desenvolvimento

### Estrutura do Projeto

```
arcee_cli/
├── __main__.py           # Ponto de entrada principal
├── agent/                # Agentes de automação
├── crew/                 # Tripulação para colaboração
├── docs/                 # Documentação
├── infrastructure/       # Infraestrutura
│   ├── config.py         # Configuração
│   ├── logging_config.py # Configuração de logging
│   ├── mcp/              # Implementação do MCP
│   └── providers/        # Provedores de serviços
```

### Documentação Adicional

- [Guia do Sistema de Logging](logging.md)
- [Manual do MCP](mcp.md)

## Contribuição

Contribuições são bem-vindas! Por favor, siga as diretrizes de contribuição no arquivo CONTRIBUTING.md.

## Licença

Este projeto está licenciado sob a licença MIT. 