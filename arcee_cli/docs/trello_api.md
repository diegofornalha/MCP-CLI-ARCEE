# Documentação da API Trello

Esta documentação descreve os endpoints disponíveis para integração com a API Trello.

## Autenticação

### auth_get_url(params)

Obter uma URL de autorização do Trello que exibirá um token de API. Este token é necessário para outras ferramentas do Trello.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| | | |

## Boards (Quadros)

### board_list(params)

Listar todos os quadros para o usuário autenticado.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| filter | enum | Filtrar quadros. Valores válidos: all, open, closed, members, organization, public, starred (padrão: all) |

### board_get(params)

Obter detalhes sobre um quadro do Trello.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| fields | string[] | Campos do quadro a incluir na resposta |
| board_id* | string | O ID do quadro a ser recuperado |

### board_create(params)

Criar um novo quadro no Trello. Nota: ao criar um quadro, algumas listas são criadas automaticamente. Verifique as listas existentes antes de criar novas.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| name* | string | Nome do quadro |
| token* | string | Token de API do Trello |
| description | string | Descrição do quadro |

### board_get_members(params)

Obter todos os membros de um quadro.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| board_id* | string | ID do quadro |

### board_add_member(params)

Adicionar um membro a um quadro por email.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| email* | string | Email do usuário a ser adicionado |
| token* | string | Token de API do Trello |
| board_id* | string | ID do quadro |
| full_name* | string | Nome completo do usuário |

### board_remove_member(params)

Remover um membro de um quadro.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| board_id* | string | ID do quadro |
| member_id* | string | ID do membro a ser removido |

### board_get_labels(params)

Obter todas as etiquetas em um quadro.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| board_id* | string | ID do quadro |

### board_get_lists(params)

Obter todas as listas em um quadro.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| filter | enum | Filtrar listas: open, closed, ou all |
| board_id* | string | ID do quadro |

### board_get_cards(params)

Obter todos os cartões em um quadro.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| board_id* | string | ID do quadro |

## Lists (Listas)

### list_create(params)

Criar uma nova lista em um quadro.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| name* | string | Nome da lista |
| token* | string | Token de API do Trello |
| board_id* | string | ID do quadro para adicionar a lista |
| position | string | Posição da lista (top, bottom, ou um número positivo) |

### list_move(params)

Mover uma lista para um quadro diferente.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| list_id* | string | ID da lista a ser movida |
| board_id* | string | ID do quadro de destino |

### list_get_cards(params)

Obter todos os cartões em uma lista com paginação.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| page | integer | Número da página a retornar (baseado em 0) |
| limit | integer | Número máximo de cartões a retornar por página (padrão: 50, máx: 1000) |
| token* | string | Token de API do Trello |
| list_id* | string | ID da lista |

### list_archive_cards(params)

Arquivar todos os cartões em uma lista.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| list_id* | string | ID da lista |

## Cards (Cartões)

### card_create(params)

Criar um novo cartão em uma lista.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| name* | string | Nome do cartão |
| token* | string | Token de API do Trello |
| list_id* | string | ID da lista para adicionar o cartão |
| description | string | Descrição do cartão |

### card_move(params)

Mover um cartão para uma lista e/ou posição diferente.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| card_id* | string | ID do cartão a ser movido |
| list_id* | string | ID da lista de destino |
| position | string | Opcional - Posição na lista (top, bottom, ou um número positivo) |

### card_get_members(params)

Obter todos os membros atribuídos a um cartão.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| card_id* | string | ID do cartão |

### card_add_member(params)

Atribuir um membro a um cartão.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| card_id* | string | ID do cartão |
| member_id* | string | ID do membro a ser atribuído |

### card_remove_member(params)

Remover um membro de um cartão.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| card_id* | string | ID do cartão |
| member_id* | string | ID do membro a ser removido |

### card_get_comments(params)

Obter todos os comentários em um cartão.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| card_id* | string | ID do cartão |

### card_add_comment(params)

Adicionar um comentário a um cartão.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| text* | string | Texto do comentário |
| token* | string | Token de API do Trello |
| card_id* | string | ID do cartão |

## Labels (Etiquetas)

### label_create(params)

Criar uma nova etiqueta em um quadro.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| name* | string | Nome da etiqueta |
| color* | enum | Cor da etiqueta (red, yellow, green, blue, purple, orange, black) |
| token* | string | Token de API do Trello |
| board_id* | string | ID do quadro |

### label_delete(params)

Excluir uma etiqueta.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| label_id* | string | ID da etiqueta a ser excluída |

## Checklists

### checklist_create(params)

Criar uma nova checklist em um cartão.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| name* | string | Nome da checklist |
| token* | string | Token de API do Trello |
| card_id* | string | ID do cartão |

### checklist_add_item(params)

Adicionar um item a uma checklist.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| name* | string | Nome do item da checklist |
| token* | string | Token de API do Trello |
| checklist_id* | string | ID da checklist |

## Comments (Comentários)

### comment_delete(params)

Excluir um comentário de um cartão.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| token* | string | Token de API do Trello |
| card_id* | string | ID do cartão |
| comment_id* | string | ID do comentário a ser excluído |

## Permissões Necessárias

### Variáveis de Configuração

| Nome | Descrição |
|------|-----------|
| api_key* | Você precisará criar um PowerUp do Trello para obter uma API Key: https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/#authorizing-a-client |

**EXEMPLO:**
```
8f3a4c1b9d2e7f5084692d3e1a5b9c4d
```

### Acesso à Rede *
api.trello.com 