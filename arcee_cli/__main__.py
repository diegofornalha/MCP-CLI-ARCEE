#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI do Arcee AI
"""

import typer
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from .infrastructure.providers import ArceeProvider

app = typer.Typer(
    help="""
    🤖 CLI do Arcee AI

    Esta CLI permite interagir com a plataforma Arcee AI.
    Use o comando 'configure' para configurar sua chave de API.
    Use o comando 'chat' para iniciar uma conversa com o modelo.
    Use o comando 'teste' para verificar a conexão com a API.
    """
)


@app.command()
def chat():
    """Inicia um chat com o Arcee AI"""
    print(
        Panel(
            "🤖 Chat com Arcee AI\n\nDigite 'sair' para encerrar.",
            title="Arcee AI",
        )
    )

    provider = ArceeProvider()
    messages = []

    while True:
        try:
            user_input = Prompt.ask("\nVocê")

            if user_input.lower() == "sair":
                break

            messages.append({"role": "user", "content": user_input})
            response = provider.generate_content_chat(messages)

            if "error" in response:
                print(f"❌ {response['error']}")
                continue

            if "choices" in response and len(response["choices"]) > 0:
                assistant_message = response["choices"][0]["message"]
                messages.append(assistant_message)
                print(f"\nAssistente: {assistant_message['content']}")
            else:
                print("❌ Resposta inválida do modelo")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            break

    print("\nAté logo! 👋")


@app.command()
def configure(
    api_key: str = typer.Option(None, help="Chave da API do Arcee"),
    org: str = typer.Option(None, help="Organização do Arcee"),
):
    """Configura a CLI do Arcee"""
    from .commands.configure import configure as configure_cmd

    configure_cmd(api_key=api_key, org=org)


@app.command()
def teste():
    """Testa a conexão com a API do Arcee"""
    try:
        print("\n🔍 Testando conexão com Arcee AI...")

        arcee = ArceeProvider()
        print(f"\n🔑 API Key configurada: {arcee.api_key[:5]}...")
        print(f"🌐 URL da API: {arcee.api_url}")
        print(f"🤖 Modelo: {arcee.model}")

        health, message = arcee.health_check()
        if health:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")

    except Exception as e:
        print(f"\n❌ Erro ao testar conexão: {str(e)}")


if __name__ == "__main__":
    app()
