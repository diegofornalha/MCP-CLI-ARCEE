# Arcee MCP Server

Servidor MCP (Model Context Protocol) do Arcee para integração com ferramentas e serviços.

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/MCP-CLI-ARCEE.git
cd MCP-CLI-ARCEE

# Instale as dependências
pip install -r requirements.txt
```

## ⚙️ Configuração

Antes de usar o servidor MCP, você precisa configurar suas chaves API do Arcee e do VeyraX. Existem duas formas de fazer isso:

1. **Configuração via CLI** (Recomendado):

   ```bash
   arcee configure
   ```

   Este comando irá guiá-lo através do processo de configuração de:

   - Chave API do Arcee (obtida em https://arcee.ai/settings)
   - Chave API do VeyraX (obtida em https://veyrax.arcee.ai/settings)

2. **Configuração manual**:
   - Crie um arquivo `.env` na raiz do projeto com:
     ```
     ARCEE_API_KEY=sua_chave_arcee
     VEYRAX_API_KEY=sua_chave_veyrax
     ```
   - Ou adicione as chaves no arquivo `~/.cursor/config.json`:
     ```json
     {
       "arceeApiKey": "sua_chave_arcee",
       "veyraxApiKey": "sua_chave_veyrax"
     }
     ```

## 🖥️ Uso do Servidor

### Iniciar o Servidor

```bash
# Iniciar na porta padrão (8081)
arcee mcp

# Iniciar em uma porta específica
arcee mcp --port 8082

# Iniciar em um host específico
arcee mcp --host 0.0.0.0 --port 8082
```

### Gerenciamento de Memórias

O servidor MCP suporta as seguintes operações de memória:

#### 1. Listar Ferramentas

```bash
arcee veyrax tools
```

#### 2. Salvar Memória

```bash
arcee veyrax call veyrax save_memory --parametros '{
  "memory": "conteúdo da memória",
  "tool": "nome_ferramenta"
}'
```

#### 3. Listar Memórias (com Paginação e Filtragem)

```bash
# Listar todas as memórias (com paginação padrão)
arcee veyrax call veyrax get_memory

# Listar memórias com filtro e paginação personalizada
arcee veyrax call veyrax get_memory --parametros '{
  "tool": "nome_ferramenta",  # Opcional: filtrar por ferramenta
  "limit": 10,                # Opcional: número máximo de resultados (padrão: 10)
  "offset": 0                 # Opcional: número de resultados para pular (padrão: 0)
}'
```

#### 4. Atualizar Memória

```bash
arcee veyrax call veyrax update_memory --parametros '{
  "id": "id_da_memoria",
  "memory": "novo conteúdo da memória",
  "tool": "nome_ferramenta"
}'
```

#### 5. Deletar Memória

```bash
arcee veyrax call veyrax delete_memory --parametros '{
  "id": "id_da_memoria"
}'
```

## 🛠️ Ferramentas Disponíveis

1. **save_memory**

   - Descrição: Salva uma memória no VeyraX
   - Parâmetros:
     - `memory`: O conteúdo da memória
     - `tool`: O nome da ferramenta associada

2. **get_memory**

   - Descrição: Obtém memórias do VeyraX com suporte a paginação e filtragem
   - Parâmetros:
     - `tool` (opcional): Nome da ferramenta para filtrar
     - `limit` (opcional): Número máximo de memórias a retornar (padrão: 10)
     - `offset` (opcional): Número de memórias a pular (padrão: 0)

3. **update_memory**

   - Descrição: Atualiza uma memória existente
   - Parâmetros:
     - `id`: ID da memória a ser atualizada
     - `memory`: Novo conteúdo da memória
     - `tool`: Nome da ferramenta associada

4. **delete_memory**
   - Descrição: Deleta uma memória
   - Parâmetros:
     - `id`: ID da memória a ser deletada

## 🔍 Solução de Problemas

Se o servidor apresentar o erro "The window terminated unexpectedly (reason: 'crashed', code: '5')", tente:

1. Verificar se não há outra instância do servidor rodando:

   ```bash
   pkill -f "arcee mcp"
   ```

2. Iniciar o servidor em uma porta diferente:

   ```bash
   arcee mcp --port 8082
   ```

3. Verificar se as chaves API estão configuradas corretamente:

   ```bash
   arcee configure
   ```

4. Verificar os logs detalhados que serão exibidos no console

## 📝 Notas

- O servidor usa FastAPI para implementação do servidor HTTP
- Logs detalhados estão habilitados por padrão
- O servidor suporta CORS para integração com outras aplicações
- A API está disponível em `http://localhost:8081` (ou a porta configurada)
- O endpoint de ferramentas está em `/tools`
- O endpoint de chamada de ferramentas está em `/tool_call`
- Todas as operações de memória suportam paginação e filtragem quando aplicável
- As respostas são retornadas em formato JSON
- Os IDs de memória são strings e devem ser preservados para operações de atualização/deleção

## 🤝 Contribuição

Sinta-se à vontade para contribuir com o projeto através de issues e pull requests.

pkill -f "arcee mcp" && sleep 2 && arcee mcp --port 8082

lsof -i :8082 | awk 'NR>1 {print $2}' | xargs kill -9 2>/dev/null; sleep 2 && arcee mcp --port 8082
