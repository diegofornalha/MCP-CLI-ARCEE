#!/usr/bin/env python3
import requests

api_key = "64b83aeb4a38f4f81b5aa69e38c75bec"
token = "ATTA990c61c1754403f36cbdd2e90697e8bef99785a0e72af0f3184a97f711472086074DFEF1"
board_id = "js3cvo6W"

url = f"https://api.trello.com/1/boards/{board_id}/lists?key={api_key}&token={token}"

response = requests.get(url)
print(f"Status code: {response.status_code}")
print(f"Response content: {response.text}")

if response.status_code == 200:
    lists = response.json()
    print(f"\nVocê tem {len(lists)} listas no seu quadro 'cli':")
    for i, lista in enumerate(lists, 1):
        print(f"{i}. {lista.get('name')}")
else:
    print(f"Erro ao consultar as listas: {response.text}")