#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comando para chat com o Arcee AI
"""

from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED
from rich.prompt import Prompt
from ..infrastructure.providers import ArceeProvider

console = Console()


def chat() -> None:
    """Inicia um chat com o Arcee AI"""
    console.print(
        Panel(
            "🤖 Chat com Arcee AI\n\nDigite 'sair' para encerrar.",
            box=ROUNDED,
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
                console.print(f"❌ {response['error']}")
                continue

            if "choices" in response and len(response["choices"]) > 0:
                assistant_message = response["choices"][0]["message"]
                messages.append(assistant_message)
                console.print(f"\nAssistente: {assistant_message['content']}")
            else:
                console.print("❌ Resposta inválida do modelo")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"❌ Erro: {str(e)}")
            break

    console.print("\nAté logo! 👋")
