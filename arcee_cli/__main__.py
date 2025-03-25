#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI do Arcee AI
"""

import typer
import json
import os
from rich import print
from rich.prompt import Prompt
import time
from getpass import getpass
from typing import Dict, Any, List, Optional, Union

from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

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

app = typer.Typer(help="CLI do Arcee AI - Converse com IA de forma simples")
console = Console()

# Provedor global para ser reutilizado em diferentes comandos
_provider = None
_agent = None
_crew = None


def get_mcp_client():
    """Obtém uma instância do cliente MCP"""
    return CursorClient()


def execute_veyrax_command(
    comando: str, ferramenta: str, metodo: str, parametros: str = None
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
                raise typer.Exit(1)

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
        raise typer.Exit(1)


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


def configure_secrets():
    """
    Configura as credenciais e preferências através de entrada interativa
    """
    print("🔧 Configuração do Arcee CLI")

    # Tenta obter as chaves atuais
    chave_atual_arcee = None
    chave_atual_veyrax = None

    try:
        provider = get_provider()
        chave_atual_arcee = provider.api_key
    except:
        pass

    try:
        cliente = CursorClient()
        chave_atual_veyrax = cliente.api_key
    except:
        pass

    # Configura chave Arcee
    print("\n1. Configuração da chave Arcee")
    if chave_atual_arcee:
        print(f"Chave Arcee atual: {chave_atual_arcee[:8]}..." + "*" * 20)
        if (
            not Prompt.ask(
                "Deseja alterar a chave Arcee?", choices=["s", "n"], default="n"
            )
            == "s"
        ):
            print("✅ Chave Arcee mantida")
        else:
            print("\nVocê pode obter sua chave Arcee em:")
            print("https://arcee.ai/settings")
            nova_chave_arcee = getpass("\nDigite sua chave Arcee: ")
            if not nova_chave_arcee:
                print("❌ Chave Arcee não pode ser vazia")
                return
            chave_atual_arcee = nova_chave_arcee
    else:
        print("\nVocê pode obter sua chave Arcee em:")
        print("https://arcee.ai/settings")
        nova_chave_arcee = getpass("\nDigite sua chave Arcee: ")
        if not nova_chave_arcee:
            print("❌ Chave Arcee não pode ser vazia")
            return
        chave_atual_arcee = nova_chave_arcee

    # Configura chave VeyraX
    print("\n2. Configuração da chave VeyraX")
    if chave_atual_veyrax:
        print(f"Chave VeyraX atual: {chave_atual_veyrax[:8]}..." + "*" * 20)
        if (
            not Prompt.ask(
                "Deseja alterar a chave VeyraX?", choices=["s", "n"], default="n"
            )
            == "s"
        ):
            print("✅ Chave VeyraX mantida")
        else:
            print("\nVocê pode obter sua chave VeyraX em:")
            print("https://veyrax.arcee.ai/settings")
            nova_chave_veyrax = getpass("\nDigite sua chave VeyraX: ")
            if not nova_chave_veyrax:
                print("❌ Chave VeyraX não pode ser vazia")
                return
            chave_atual_veyrax = nova_chave_veyrax
    else:
        print("\nVocê pode obter sua chave VeyraX em:")
        print("https://veyrax.arcee.ai/settings")
        nova_chave_veyrax = getpass("\nDigite sua chave VeyraX: ")
        if not nova_chave_veyrax:
            print("❌ Chave VeyraX não pode ser vazia")
            return
        chave_atual_veyrax = nova_chave_veyrax

    # Decide onde salvar
    print("\nOnde deseja salvar a configuração?")
    print("1. Configuração global do Cursor (~/.cursor/config.json)")
    print("2. Arquivo .env no projeto")

    opcao = Prompt.ask("Escolha", choices=["1", "2"], default="1")

    if opcao == "1":
        # Salva no config.json do Cursor
        config = {}
        cursor_config = os.path.expanduser("~/.cursor/config.json")

        # Carrega configuração existente se houver
        if os.path.exists(cursor_config):
            try:
                with open(cursor_config) as f:
                    config = json.load(f)
            except:
                pass

        # Atualiza as chaves
        if chave_atual_arcee:
            config["arceeApiKey"] = chave_atual_arcee
        if chave_atual_veyrax:
            config["veyraxApiKey"] = chave_atual_veyrax

        # Salva a configuração
        with open(cursor_config, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Configuração salva em {cursor_config}")

    else:
        # Salva no .env do projeto
        env_content = []

        # Carrega conteúdo existente se houver
        if os.path.exists(".env"):
            with open(".env") as f:
                env_content = f.readlines()

        # Remove linhas existentes com as chaves
        env_content = [
            line
            for line in env_content
            if not line.startswith(("ARCEE_API_KEY=", "VEYRAX_API_KEY="))
        ]

        # Adiciona as novas chaves
        if chave_atual_arcee:
            env_content.append(f"ARCEE_API_KEY={chave_atual_arcee}\n")
        if chave_atual_veyrax:
            env_content.append(f"VEYRAX_API_KEY={chave_atual_veyrax}\n")

        # Salva o arquivo
        with open(".env", "w") as f:
            f.writelines(env_content)

        print("✅ Configuração salva no arquivo .env")

    print("\n✨ Configuração concluída com sucesso!")


def execute_teste_command():
    """
    Executa um teste de funcionalidade
    """
    print("Testando funcionalidade")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Variáveis de ambiente: {os.environ.get('PATH')}")


def iniciar_chat():
    """
    Inicia uma conversa com a IA usando o CLI
    """
    print("🤖 Arcee AI - Chat Interativo")
    print("\nDigite 'sair' para encerrar o chat")
    print("Comandos disponíveis:")
    print("  veyrax:tools - Lista as ferramentas disponíveis")
    print("  veyrax:memory - Lista todas as memórias")
    print("  veyrax:memory save <conteúdo> <ferramenta> - Salva uma memória")
    print(
        "  veyrax:memory get [ferramenta] [limit] [offset] - Lista memórias com filtro e paginação"
    )
    print("  veyrax:memory update <id> <conteúdo> <ferramenta> - Atualiza uma memória")
    print("  veyrax:memory delete <id> - Deleta uma memória")
    print("  cursor: <pergunta> - Envia uma pergunta diretamente para o Cursor Agent")

    # Configura a porta do MCP
    os.environ["MCP_PORT"] = "8082"  # Garante que use a porta correta

    historial = []
    cliente = CursorClient()  # Inicializa o cliente uma vez só

    while True:
        try:
            # Obter entrada do usuário
            mensagem = Prompt.ask("\n💬 Você")

            if mensagem.lower() in ["sair", "exit", "quit", "q"]:
                print("👋 Até logo!")
                break

            # Verifica se é um comando para listar memórias em linguagem natural
            if mensagem.lower() in [
                "lista todas as memórias",
                "listar memórias",
                "mostrar memórias",
                "ver memórias",
                "memórias",
                "lista memórias",
                "list memories",
                "show memories",
            ]:
                print("\n🤖 Arcee AI")
                try:
                    resultado = cliente.get_memories()
                    if "error" in resultado:
                        print(f"❌ Erro ao listar memórias: {resultado['error']}")
                    else:
                        print("✅ Memórias encontradas:")
                        if isinstance(resultado, dict) and "content" in resultado:
                            content = resultado.get("content", [])
                            if (
                                content
                                and isinstance(content, list)
                                and len(content) > 0
                            ):
                                text = content[0].get("text", "")
                                try:
                                    # Tenta parsear o texto como JSON
                                    data = json.loads(text)
                                    print(
                                        json.dumps(data, indent=2, ensure_ascii=False)
                                    )
                                except:
                                    # Se não for JSON, imprime como texto
                                    print(text)
                            else:
                                print(
                                    json.dumps(resultado, indent=2, ensure_ascii=False)
                                )
                        else:
                            print(json.dumps(resultado, indent=2, ensure_ascii=False))
                    continue
                except Exception as e:
                    print(f"❌ Erro ao executar comando: {str(e)}")
                    continue

            # Verifica se é um comando para o Cursor Agent
            if mensagem.lower().startswith("cursor:"):
                query = mensagem[7:].strip()  # Remove "cursor:" do início
                print("\n🤖 Arcee AI")
                try:
                    resultado = cliente.query_cursor_agent(query)
                    if "error" in resultado:
                        print(f"❌ Erro ao executar Cursor Agent: {resultado['error']}")
                    else:
                        if isinstance(resultado, dict):
                            if resultado.get("success"):
                                print(resultado["response"])
                            else:
                                print(
                                    f"❌ Erro: {resultado.get('error', 'Erro desconhecido')}"
                                )
                        else:
                            print(resultado)
                    continue
                except Exception as e:
                    print(f"❌ Erro ao executar comando: {str(e)}")
                    continue

            # Verifica se é um comando veyrax
            if mensagem.lower().startswith(("veyrax:", "ferramenta veyrax")):
                print("\n🤖 Arcee AI")
                try:
                    # Remove o prefixo e divide os argumentos
                    if mensagem.lower().startswith("veyrax:"):
                        args = mensagem[7:].strip().split()
                    else:
                        args = (
                            mensagem[16:].strip().split()
                        )  # Remove "ferramenta veyrax"

                    if not args:
                        # Mostra ajuda se não houver argumentos
                        print("Comandos VeyraX disponíveis:")
                        print("  veyrax:tools - Lista todas as ferramentas")
                        print("  veyrax:memory - Lista todas as memórias")
                        print(
                            "  veyrax:memory save <conteúdo> <ferramenta> - Salva uma memória"
                        )
                        print(
                            "  veyrax:memory get [ferramenta] [limit] [offset] - Lista memórias com filtro"
                        )
                        print(
                            "  veyrax:memory update <id> <conteúdo> <ferramenta> - Atualiza uma memória"
                        )
                        print("  veyrax:memory delete <id> - Deleta uma memória")
                        continue

                    comando = args[0].lower()

                    if comando == "tools":
                        # Lista ferramentas
                        resultado = cliente.get_tools()
                        if "error" in resultado:
                            print(
                                f"❌ Erro ao listar ferramentas: {resultado['error']}"
                            )
                        else:
                            print("✅ Ferramentas disponíveis:")
                            print(json.dumps(resultado, indent=2, ensure_ascii=False))

                    elif comando == "memory":
                        if len(args) < 2:
                            # Lista todas as memórias com paginação padrão
                            resultado = cliente.get_memories()
                        else:
                            subcomando = args[1].lower()

                            if subcomando == "save" and len(args) >= 4:
                                # Salva uma memória
                                resultado = cliente.save_memory(args[2], args[3])

                            elif subcomando == "get":
                                # Prepara parâmetros de paginação e filtro
                                tool = args[2] if len(args) > 2 else None
                                limit = int(args[3]) if len(args) > 3 else 10
                                offset = int(args[4]) if len(args) > 4 else 0
                                resultado = cliente.get_memories(tool, limit, offset)

                            elif subcomando == "update" and len(args) >= 5:
                                # Atualiza uma memória
                                resultado = cliente.update_memory(
                                    args[2], args[3], args[4]
                                )

                            elif subcomando == "delete" and len(args) >= 3:
                                # Deleta uma memória
                                resultado = cliente.delete_memory(args[2])

                            else:
                                print("❌ Comando inválido ou parâmetros insuficientes")
                                print("Uso:")
                                print("  veyrax:memory - Lista todas as memórias")
                                print(
                                    "  veyrax:memory save <conteúdo> <ferramenta> - Salva uma memória"
                                )
                                print(
                                    "  veyrax:memory get [ferramenta] [limit] [offset] - Lista memórias com filtro"
                                )
                                print(
                                    "  veyrax:memory update <id> <conteúdo> <ferramenta> - Atualiza uma memória"
                                )
                                print(
                                    "  veyrax:memory delete <id> - Deleta uma memória"
                                )
                                continue

                        if "error" in resultado:
                            print(f"❌ Erro ao executar comando: {resultado['error']}")
                        else:
                            print("✅ Resultado:")
                            if isinstance(resultado, dict) and "content" in resultado:
                                content = resultado.get("content", [])
                                if (
                                    content
                                    and isinstance(content, list)
                                    and len(content) > 0
                                ):
                                    text = content[0].get("text", "")
                                    try:
                                        # Tenta parsear o texto como JSON
                                        data = json.loads(text)
                                        print(
                                            json.dumps(
                                                data, indent=2, ensure_ascii=False
                                            )
                                        )
                                    except:
                                        # Se não for JSON, imprime como texto
                                        print(text)
                                else:
                                    print(
                                        json.dumps(
                                            resultado, indent=2, ensure_ascii=False
                                        )
                                    )
                            else:
                                print(
                                    json.dumps(resultado, indent=2, ensure_ascii=False)
                                )

                    else:
                        print("❌ Comando desconhecido")
                        print("Comandos disponíveis:")
                        print("  veyrax:tools - Lista todas as ferramentas")
                        print("  veyrax:memory - Lista todas as memórias")
                        print(
                            "  veyrax:memory save <conteúdo> <ferramenta> - Salva uma memória"
                        )
                        print(
                            "  veyrax:memory get [ferramenta] [limit] [offset] - Lista memórias com filtro"
                        )
                        print(
                            "  veyrax:memory update <id> <conteúdo> <ferramenta> - Atualiza uma memória"
                        )
                        print("  veyrax:memory delete <id> - Deleta uma memória")

                except Exception as e:
                    print(f"❌ Erro ao executar comando: {str(e)}")
                continue

            # Processa a mensagem normal
            historial.append({"role": "user", "content": mensagem})

            # Obtém o provedor e envia a mensagem
            provider = get_provider()
            resposta = provider.chat(mensagem, historial)

            print(f"\n🤖 Arcee AI")
            print(resposta)

            historial.append({"role": "assistant", "content": resposta})

        except KeyboardInterrupt:
            print("\n👋 Chat interrompido. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {str(e)}")
            continue


def iniciar_agente():
    """
    Inicia o agente automatizado para auxiliar com tarefas
    """
    from arcee_cli.agent.arcee_agent import ArceeAgent

    print("🤖 Arcee Agent ativado")

    # Cria e executa o agente
    agente = ArceeAgent()
    agente.executar()


@app.command()
def chat(
    mensagem: str = typer.Argument(
        None, help="Mensagem para enviar diretamente ao chat"
    ),
    cursor: bool = typer.Option(
        False, "--cursor", "-c", help="Envia a mensagem para o Cursor Agent"
    ),
):
    """Inicia uma conversa com a IA ou envia uma mensagem direta"""
    if mensagem:
        if cursor:
            try:
                cliente = CursorClient()
                sucesso, resultado = cliente.tool_call(
                    "cursor_agent", "query", {"query": mensagem}
                )

                if not sucesso:
                    print(f"❌ Erro ao executar Cursor Agent: {resultado}")
                else:
                    if isinstance(resultado, dict):
                        if resultado.get("success"):
                            print(resultado["response"])
                        else:
                            print(
                                f"❌ Erro: {resultado.get('error', 'Erro desconhecido')}"
                            )
                    else:
                        print(resultado)
            except Exception as e:
                print(f"❌ Erro ao executar comando: {str(e)}")
        else:
            # Processa a mensagem normal
            provider = get_provider()
            resposta = provider.chat(mensagem)
            print(f"\n🤖 Arcee AI")
            print(resposta)
    else:
        iniciar_chat()


@app.command()
def configure():
    """Configura as credenciais e preferências"""
    configure_secrets()


@app.command()
def teste():
    """Executa testes de funcionalidade"""
    execute_teste_command()


@app.command()
def veyrax(
    comando: Optional[str] = typer.Argument(None, help="Comando (tools, call)"),
    ferramenta: Optional[str] = typer.Argument(
        None, help="Nome da ferramenta (para comando call)"
    ),
    metodo: Optional[str] = typer.Argument(
        None, help="Nome do método (para comandos call)"
    ),
    parametros: Optional[str] = typer.Option(
        None, "--parametros", "-p", help="Parâmetros em formato JSON"
    ),
):
    """
    Executa comandos relacionados ao MCP Server.

    Exemplos:

    \b
    # Listar ferramentas
    arcee veyrax tools

    \b
    # Salvar memória
    arcee veyrax call veyrax save_memory --parametros '{"memory": "conteúdo", "tool": "nome_ferramenta"}'

    \b
    # Listar memórias com paginação
    arcee veyrax call veyrax get_memory --parametros '{"tool": "nome_ferramenta", "limit": 10, "offset": 0}'

    \b
    # Atualizar memória
    arcee veyrax call veyrax update_memory --parametros '{"id": "id_memoria", "memory": "novo_conteudo", "tool": "nome_ferramenta"}'

    \b
    # Deletar memória
    arcee veyrax call veyrax delete_memory --parametros '{"id": "id_memoria"}'
    """
    execute_veyrax_command(comando, ferramenta, metodo, parametros)


@app.command()
def agent():
    """Inicia uma conversa com a IA usando o Arcee Agent"""
    iniciar_agente()


@app.command()
def mcp(
    host: str = typer.Option("localhost", help="Host do servidor MCP"),
    port: int = typer.Option(8081, help="Porta do servidor MCP"),
):
    """
    Inicia o servidor MCP do Arcee.

    Exemplo:
    arcee mcp --host localhost --port 8081
    """
    import os
    from arcee_cli.infrastructure.mcp.mcp_server import run_server

    # Define as variáveis de ambiente para o servidor
    os.environ["MCP_HOST"] = host
    os.environ["MCP_PORT"] = str(port)

    # Inicia o servidor com as configurações personalizadas
    try:
        run_server(host, port)
    except Exception as e:
        print(f"❌ Erro ao iniciar o servidor: {str(e)}")
        raise


if __name__ == "__main__":
    app()
