# Arcee CLI

CLI para interagir com a API da Arcee AI.

## Instalação

```bash
pip install arcee-cli
```

## Configuração

Antes de usar, configure sua chave API:

```bash
arcee configure
```

Ou defina a variável de ambiente:

```bash
export ARCEE_API_KEY="sua-chave-api"
```

## Uso

### Chat

Inicie uma conversa com a IA:

```bash
arcee chat
```

### Teste

Teste a conexão com a API:

```bash
arcee teste
```

## Variáveis de Ambiente

- `ARCEE_API_KEY`: Sua chave API da Arcee
- `ARCEE_MODEL`: Modelo a ser usado (padrão: "auto")
- `ARCEE_ORG`: ID da organização (opcional)
