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
from rich.table import Table
import subprocess
import os
import signal
import sys

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

# Cria um grupo de comandos para o MCP
mcp_app = typer.Typer(
    help="""
    🔌 Gerenciamento de ferramentas MCP

    Comandos para gerenciar as ferramentas do MCP.
    """
)
app.add_typer(mcp_app, name="mcp")

console = Console()

# Provedor global para ser reutilizado em diferentes comandos
_provider = None
_agent = None
_crew = None
_mcp_processo = None


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

            # O ArceeProvider retorna a resposta na chave 'text'
            if "text" in response:
                content = response["text"]
                # Adiciona a resposta ao histórico
                messages.append({"role": "assistant", "content": content})
                print(f"\nAssistente: {content}")
            else:
                # Fallback para o formato antigo (caso haja alterações futuras)
                print("⚠️ Formato de resposta não reconhecido")
                print(f"Chaves disponíveis: {list(response.keys())}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            import traceback
            traceback.print_exc()
            break

    print("\nAté logo! 👋")


@app.command()
def configure(
    api_key: str = typer.Option(None, help="Chave da API do Arcee"),
    org: str = typer.Option(None, help="Organização do Arcee"),
):
    """Configura a CLI do Arcee"""
    config_setup(api_key=api_key, org=org)


@mcp_app.command("iniciar")
def iniciar_mcp(
    porta: int = typer.Option(8083, help="Porta para o servidor MCP personalizado"),
    substituir_padrao: bool = typer.Option(
        True, help="Substitui a porta padrão do MCP nas requisições"
    ),
):
    """Inicia o servidor MCP personalizado com filtragem de ferramentas"""
    global _mcp_processo

    # Verifica se já existe um processo em execução
    if _mcp_processo and _mcp_processo.poll() is None:
        print("❌ Servidor MCP já está em execução")
        return

    try:
        # Define a porta do MCP personalizado
        os.environ["MCP_PORT"] = str(porta)

        # Inicia o servidor em processo separado
        from arcee_cli.infrastructure.mcp.server import iniciar_servidor
        
        print(f"🚀 Iniciando servidor MCP personalizado na porta {porta}...")
        
        # Usa multiprocessing para iniciar o servidor
        import multiprocessing
        processo = multiprocessing.Process(target=iniciar_servidor, args=("0.0.0.0", porta))
        processo.daemon = True
        processo.start()
        
        print(f"✅ Servidor MCP personalizado iniciado com sucesso (PID: {processo.pid})")
        print("📋 Use 'arcee mcp listar' para ver as ferramentas disponíveis")
        
        # Guarda o processo
        _mcp_processo = processo
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor MCP: {e}")
        raise typer.Exit(1) from e


@mcp_app.command("parar")
def parar_mcp():
    """Para o servidor MCP personalizado"""
    global _mcp_processo
    
    if not _mcp_processo:
        print("❌ Servidor MCP não está em execução")
        return
        
    try:
        print("🛑 Parando servidor MCP personalizado...")
        
        # Termina o processo
        _mcp_processo.terminate()
        _mcp_processo.join(timeout=5)
        
        if _mcp_processo.is_alive():
            print("⚠️ Processo não terminou normalmente, forçando encerramento...")
            _mcp_processo.kill()
            
        print("✅ Servidor MCP personalizado parado com sucesso")
        _mcp_processo = None
    except Exception as e:
        print(f"❌ Erro ao parar servidor MCP: {e}")
        raise typer.Exit(1) from e


@mcp_app.command("listar")
def listar_ferramentas():
    """Lista todas as ferramentas disponíveis no MCP"""
    try:
        # Obtém o cliente MCP
        client = get_mcp_client()
        
        # Importa funções de gerenciamento
        from arcee_cli.infrastructure.mcp.mcp_config import (
            listar_ferramentas_disponiveis,
            filtrar_ferramentas,
            obter_ferramentas_ativas,
            obter_ferramentas_inativas,
        )
        
        print("🔍 Obtendo lista de ferramentas disponíveis...")
        todas_ferramentas = listar_ferramentas_disponiveis(client)
        
        # Filtra as ferramentas
        ferramentas_filtradas = filtrar_ferramentas(todas_ferramentas)
        ferramentas_ativas = ferramentas_filtradas["ativas"]
        ferramentas_inativas = ferramentas_filtradas["inativas"]
        
        # Cria a tabela
        tabela = Table(title="🔌 Ferramentas MCP")
        tabela.add_column("Nome", style="cyan")
        tabela.add_column("Status", style="green")
        
        # Adiciona as ferramentas ativas
        for ferramenta in ferramentas_ativas:
            tabela.add_row(ferramenta, "✅ Ativa")
            
        # Adiciona as ferramentas inativas
        for ferramenta in ferramentas_inativas:
            tabela.add_row(ferramenta, "❌ Inativa")
            
        # Exibe a tabela
        console.print(tabela)
        
    except Exception as e:
        print(f"❌ Erro ao listar ferramentas: {e}")
        raise typer.Exit(1) from e


@mcp_app.command("ativar")
def ativar_ferramenta(
    nome: str = typer.Argument(..., help="Nome da ferramenta para ativar")
):
    """Ativa uma ferramenta do MCP"""
    try:
        from arcee_cli.infrastructure.mcp.mcp_config import ativar_ferramenta as ativar
        
        print(f"🔌 Ativando ferramenta '{nome}'...")
        if ativar(nome):
            print(f"✅ Ferramenta '{nome}' ativada com sucesso")
        else:
            print(f"❌ Erro ao ativar ferramenta '{nome}'")
            
    except Exception as e:
        print(f"❌ Erro ao ativar ferramenta: {e}")
        raise typer.Exit(1) from e


@mcp_app.command("desativar")
def desativar_ferramenta(
    nome: str = typer.Argument(..., help="Nome da ferramenta para desativar")
):
    """Desativa uma ferramenta do MCP"""
    try:
        from arcee_cli.infrastructure.mcp.mcp_config import desativar_ferramenta as desativar
        
        print(f"🔌 Desativando ferramenta '{nome}'...")
        if desativar(nome):
            print(f"✅ Ferramenta '{nome}' desativada com sucesso")
        else:
            print(f"❌ Erro ao desativar ferramenta '{nome}'")
            
    except Exception as e:
        print(f"❌ Erro ao desativar ferramenta: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        # Certifica-se de que os processos são encerrados
        if _mcp_processo and hasattr(_mcp_processo, 'terminate'):
            _mcp_processo.terminate()
        
        print("\n👋 Programa encerrado pelo usuário")
        sys.exit(0)
