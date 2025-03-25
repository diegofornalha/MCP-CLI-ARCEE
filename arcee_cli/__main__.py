#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI do Arcee AI
"""

from typing import Optional
import json
import typer
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.console import Console

from arcee_cli.infrastructure.providers.arcee_provider import ArceeProvider
from arcee_cli.infrastructure.config import configure as config_setup
from arcee_cli.infrastructure.providers.provider_factory import get_provider
from arcee_cli.agent.arcee_agent import ArceeAgent
from arcee_cli.infrastructure.mcp.cursor_client import CursorClient

# Importação condicional de crewAI
try:
    from arcee_cli.crew.arcee_crew import ArceeCrew

    CREW_AVAILABLE = True
except ImportError:
    CREW_AVAILABLE = False

app = typer.Typer(
    help="""
    🤖 CLI do Arcee AI

    Esta CLI permite interagir com a plataforma Arcee AI.
    Use o comando 'configure' para configurar sua chave de API.
    Use o comando 'chat' para iniciar uma conversa com o modelo.
    Use o comando 'teste' para verificar a conexão com a API.
    """
)

console = Console()

# Provedor global para ser reutilizado em diferentes comandos
_provider = None
_agent = None
_crew = None


def get_mcp_client():
    """Obtém uma instância do cliente MCP"""
    return CursorClient()


def execute_veyrax_command(
    comando: str, ferramenta: str, metodo: str, parametros: Optional[str] = None
):
    """Executa um comando do VeyraX"""
    try:
        # Obtém o cliente MCP
        client = get_mcp_client()

        # Processa os parâmetros
        params = {}
        if parametros:
            try:
                params = json.loads(parametros)
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao processar parâmetros JSON: {e}")
                raise typer.Exit(1) from e

        # Executa o comando
        print(f"🚀 Chamando ferramenta '{ferramenta}' método '{metodo}'...")
        result = client.tool_call(ferramenta, metodo, params)

        # Processa o resultado
        if isinstance(result, dict) and "error" in result:
            print(f"❌ Erro ao executar ferramenta: {result['error']}")
            raise typer.Exit(1)

        print("✅ Resultado da chamada:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        raise typer.Exit(1) from e


def get_provider():
    """
    Obtém ou cria um provedor global para comunicação com a API

    Returns:
        ArceeProvider: Provedor para comunicação com a API
    """
    global _provider
    if _provider is None:
        _provider = ArceeProvider()
    return _provider


def get_agent():
    """
    Obtém ou cria um agente global para facilitar o trabalho com ferramentas

    Returns:
        ArceeAgent: Agente para automatizar o trabalho com ferramentas
    """
    global _agent
    if _agent is None:
        _agent = ArceeAgent()
    return _agent


def get_crew():
    """
    Obtém ou cria uma tripulação global para trabalho coordenado

    Returns:
        ArceeCrew: Tripulação para trabalho coordenado ou None se não disponível
    """
    global _crew
    if not CREW_AVAILABLE:
        return None

    if _crew is None:
        _crew = ArceeCrew()
    return _crew


@app.command()
def chat():
    """Inicia um chat com o Arcee AI"""
    print(
        Panel(
            "🤖 Chat com Arcee AI\n\nDigite 'sair' para encerrar.",
            title="Arcee AI",
        )
    )

    provider = get_provider()
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

            if "choices" in response and response["choices"]:
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
    config_setup(api_key=api_key, org=org)


if __name__ == "__main__":
    app()
