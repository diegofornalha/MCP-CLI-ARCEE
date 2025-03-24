#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI do Arcee AI
"""

import typer
from rich import print
from rich.prompt import Prompt

from arcee_cli.infrastructure.providers.arcee_provider import ArceeProvider
from arcee_cli.infrastructure.config import configure

app = typer.Typer(help="CLI do Arcee AI - Converse com IA de forma simples")


@app.command()
def chat():
    """Inicia uma conversa com a IA"""
    provider = ArceeProvider()

    # Verifica se temos uma chave API configurada
    health_ok, msg = provider.health_check()
    if not health_ok:
        print(f"❌ {msg}")
        return

    print("🤖 Iniciando chat com Arcee AI...")
    print("Digite 'sair' para encerrar o chat\n")

    # Lista de mensagens para manter o contexto
    messages = []

    while True:
        # Obtém entrada do usuário
        user_input = Prompt.ask("👤 Você")

        if user_input.lower() == "sair":
            print("\n👋 Até logo!")
            break

        # Adiciona mensagem do usuário ao contexto
        messages.append({"role": "user", "content": user_input})

        try:
            # Gera resposta
            response = provider.generate_content_chat(messages)

            if "error" in response:
                print(f"❌ {response['error']}")
                continue

            # Extrai a resposta da IA
            if "text" in response:
                print(f"\n🤖 Arcee: {response['text']}\n")

                # Adiciona resposta ao contexto
                messages.append({"role": "assistant", "content": response["text"]})

                # Exibe informações do modelo se disponíveis
                if response.get("selected_model"):
                    print("\n--- Informações do Modelo ---")
                    print(
                        f"Modelo selecionado: {response.get('selected_model', 'desconhecido')}"
                    )
                    print(
                        f"Razão da seleção: {response.get('selection_reason', 'não informada')}"
                    )
                    print(
                        f"Tipo de tarefa: {response.get('task_type', 'não informado')}"
                    )
                    print(f"Domínio: {response.get('domain', 'não informado')}")
                    print(
                        f"Complexidade: {response.get('complexity', 'não informada')}"
                    )
                    print("-----------------------------")
            else:
                print("❌ Resposta inválida da API")

        except Exception as e:
            print(f"❌ Erro ao processar resposta: {str(e)}")


@app.command()
def configure():
    """Configura a chave API e organização"""
    from arcee_cli.infrastructure.config import configure

    configure()


@app.command()
def teste():
    """Testa a conexão com a API"""
    provider = ArceeProvider()
    health_ok, msg = provider.health_check()

    print(f"🔑 Chave API: {'Configurada' if health_ok else 'Não configurada'}")
    print(f"🤖 Modelo: {provider.model}")

    if health_ok:
        print("✅ Teste concluído com sucesso!")
    else:
        print(f"❌ {msg}")


if __name__ == "__main__":
    app()
