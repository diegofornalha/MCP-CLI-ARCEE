# MCP Server

Servidor MCP (Model Control Protocol) para integração com diferentes serviços, incluindo VeyraX e Airtable.

## Configuração

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente no arquivo `.env`:
```env
VEYRAX_API_KEY=sua_chave_api_veyrax
VEYRAX_BASE_URL=https://api.veyrax.com
AIRTABLE_API_KEY=sua_chave_api_airtable
```

## Executando o Servidor

Para iniciar o servidor:

```bash
python src/server.py
```

O servidor estará disponível em `http://localhost:3000`.

## Endpoints

### Health Check
- GET `/health`
- Retorna o status de saúde do servidor

### MCP API
- POST `/api/mcp`
- Processa requisições MCP para diferentes serviços

#### Exemplo de Requisição VeyraX:
```json
{
    "tool": "veyrax",
    "method": "get_tools",
    "parameters": {}
}
```

#### Exemplo de Requisição Airtable:
```json
{
    "tool": "airtable",
    "method": "list_bases",
    "parameters": {}
}
```

## Serviços Suportados

### VeyraX
- `get_tools`: Lista todas as ferramentas disponíveis
- `tool_call`: Executa uma ferramenta específica

### Airtable
- `list_bases`: Lista todas as bases disponíveis
- `list_tables`: Lista todas as tabelas de uma base
- `list_records`: Lista todos os registros de uma tabela

## Licença

MIT 