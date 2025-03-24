# Arcee CLI

CLI para interagir com a API da Arcee AI Client.

## Instalação

```bash
pip install arcee-cli
```

## Configuração

Existem duas formas de configurar sua chave API:

### 1. Configuração via comando (Recomendado)

Esta é a forma recomendada e tem prioridade sobre o arquivo `.env`:

```bash
arcee configure
```

### 2. Variáveis de ambiente

Alternativamente, você pode definir a chave API no arquivo `.env` na raiz do projeto:

```env
ARCEE_API_KEY=sua-chave-api
ARCEE_MODEL=auto
```

**Observação**: A chave configurada via `arcee configure` sempre terá prioridade sobre a definida no arquivo `.env`.

## Uso

### Chat

Inicie uma conversa com a IA:

```bash
arcee chat
```

### Configure

Configure sua chave API interativamente:

```bash
arcee configure
```

### Teste

Teste a conexão com a API:

```bash
arcee teste
```
