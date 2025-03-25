cons# Sistema de Logging do Arcee CLI

Este documento descreve como usar o sistema de logging do Arcee CLI.

## Visão Geral

O sistema de logging do Arcee CLI foi projetado para:

1. Registrar informações de debug e erros em arquivos de log
2. Manter o console limpo, exibindo apenas mensagens relevantes para o usuário
3. Facilitar a depuração de problemas

## Configuração

O sistema de logging está centralizado no módulo `arcee_cli.infrastructure.logging_config` e oferece:

- Logging em arquivo com rotação (máximo de 10MB por arquivo, mantendo 5 arquivos)
- Logging no console para mensagens importantes
- Níveis de logging configuráveis

## Como Usar

### 1. Importar o Módulo

```python
from arcee_cli.infrastructure.logging_config import configurar_logging, obter_logger
```

### 2. Configurar o Logger (uma vez na inicialização)

```python
# Na inicialização da aplicação (geralmente em __main__.py)
configurar_logging()
```

### 3. Obter um Logger para Cada Módulo

```python
# Em cada módulo que precisa de logging
logger = obter_logger("nome_do_modulo")
```

### 4. Usar o Logger

```python
# Níveis de logging
logger.debug("Mensagem detalhada para depuração")
logger.info("Informação geral importante")
logger.warning("Alerta sobre um possível problema")
logger.error("Erro que não interrompeu a execução")
logger.critical("Erro grave que pode interromper o sistema")
logger.exception("Registra erro com stack trace (usar dentro de blocos except)")
```

## Arquivo de Log

Os logs são armazenados em:

```
~/.arcee/logs/arcee.log
```

## Níveis de Log

- **DEBUG**: Informações detalhadas, úteis para depuração
- **INFO**: Confirmação de que as coisas estão funcionando conforme esperado
- **WARNING**: Indicação de que algo inesperado aconteceu ou poderá acontecer no futuro
- **ERROR**: Erros que não impediram que o programa continuasse funcionando
- **CRITICAL**: Erros graves que podem impedir o funcionamento do programa

## Controle de Logs de Bibliotecas Externas

Por padrão, o sistema de logging configura bibliotecas externas para evitar poluição do console:

- **OpenAI**: As mensagens `HTTP Request: POST https://models.arcee.ai/v1/chat/completions "HTTP/1.1 200 OK"` são filtradas para manter o console limpo durante o chat. Essas informações ainda são registradas no arquivo de log se o nível DEBUG estiver ativado.

Para usar essa funcionalidade em novos módulos:

```python
from arcee_cli.infrastructure.logging_config import configurar_loggers_bibliotecas

# Configure loggers de bibliotecas
configurar_loggers_bibliotecas()
```

## Exemplos

**Registrando uma ação importante:**
```python
logger.info(f"Iniciando servidor MCP na porta {porta}")
```

**Registrando um erro:**
```python
try:
    # Código que pode falhar
    result = executar_operacao()
except Exception as e:
    logger.error(f"Erro ao executar operação: {e}")
    # Tratamento do erro
```

**Registrando erro com stack trace:**
```python
try:
    # Código que pode falhar
    result = executar_operacao()
except Exception as e:
    logger.exception(f"Erro crítico ao executar operação")
    # Tratamento do erro
```

## Dicas

1. Use `logger.debug()` para informações úteis apenas durante a depuração
2. Use `logger.info()` para ações significativas do sistema
3. Use `logger.warning()` para situações inesperadas que não são erros
4. Use `logger.error()` e `logger.critical()` para registrar problemas reais
5. Use `logger.exception()` dentro de blocos `except` para registrar o stack trace 