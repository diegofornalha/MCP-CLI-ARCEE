#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI do Arcee AI
"""

import typer
from rich import print
from rich.prompt import Prompt

from arcee_cli.infrastructure.providers.arcee_provider import ArceeProvider
from arcee_cli.infrastructure.config import configure as config_setup

app = typer.Typer(help="CLI do Arcee AI - Converse com IA de forma simples")

# Provedor global para ser reutilizado em diferentes comandos
_provider = None


def get_provider():
    """Retorna um provedor global ou cria um novo se não existir"""
    global _provider
    if _provider is None:
        try:
            _provider = ArceeProvider()
        except ValueError as e:
            print(f"❌ {str(e)}")
    return _provider


@app.command()
def chat():
    """Inicia uma conversa com a IA"""
    provider = get_provider()
    if provider is None:
        return

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

                # Exibe apenas informações do modelo que estão disponíveis
                if response.get("selected_model"):
                    print("\n--- Informações do Modelo ---")
                    print(
                        f"Modelo selecionado: {response.get('selected_model', 'desconhecido')}"
                    )

                    # Exibe apenas se houver informação
                    if (
                        response.get("selection_reason")
                        and response.get("selection_reason") != "não informada"
                    ):
                        print(f"Razão da seleção: {response.get('selection_reason')}")

                    if (
                        response.get("task_type")
                        and response.get("task_type") != "não informado"
                    ):
                        print(f"Tipo de tarefa: {response.get('task_type')}")

                    if (
                        response.get("domain")
                        and response.get("domain") != "não informado"
                    ):
                        print(f"Domínio: {response.get('domain')}")

                    if (
                        response.get("complexity")
                        and response.get("complexity") != "não informada"
                    ):
                        print(f"Complexidade: {response.get('complexity')}")

                    # Exibe informações de tokens se disponíveis
                    if response.get("tokens_total", 0) > 0:
                        print(f"Tokens de entrada: {response.get('tokens_prompt', 0)}")
                        print(
                            f"Tokens de saída: {response.get('tokens_completion', 0)}"
                        )
                        print(f"Total de tokens: {response.get('tokens_total', 0)}")

                    # Exibe tamanho da resposta
                    if response.get("response_length", 0) > 0:
                        print(
                            f"Tamanho da resposta: {response.get('response_length')} caracteres"
                        )
                        print(f"Palavras: {response.get('response_words')}")

                    print("-----------------------------")
            else:
                print("❌ Resposta inválida da API")

        except Exception as e:
            print(f"❌ Erro ao processar resposta: {str(e)}")


@app.command()
def configure():
    """Configura a chave API e organização"""
    global _provider

    # Executa a configuração
    config_setup()

    # Reinicia o provedor para usar a nova configuração
    _provider = None
    provider = get_provider()

    if provider:
        print(
            "✅ Configuração aplicada! Você já pode usar o chat com a nova chave API."
        )


@app.command()
def teste():
    """Testa a conexão com a API"""
    provider = get_provider()
    if provider is None:
        return

    health_ok, msg = provider.health_check()

    print(f"🔑 Chave API: {'Configurada' if health_ok else 'Não configurada'}")
    print(f"🤖 Modelo: {provider.model}")

    if health_ok:
        print("✅ Teste concluído com sucesso!")
    else:
        print(f"❌ {msg}")


if __name__ == "__main__":
    app()
