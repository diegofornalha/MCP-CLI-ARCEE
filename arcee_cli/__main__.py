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
from rich.syntax import Syntax
import subprocess
import os
import signal
import sys
import logging
import shutil
from datetime import datetime
import requests
import re

from arcee_cli.infrastructure.logging_config import configurar_logging, obter_logger, LOG_DIR, LOG_FILE
from arcee_cli.infrastructure.providers.arcee_provider import ArceeProvider
from arcee_cli.infrastructure.config import configure as config_setup
from arcee_cli.infrastructure.providers.provider_factory import get_provider as get_provider_factory
from arcee_cli.agent.arcee_agent import ArceeAgent

# Configuração de logging
configurar_logging()
logger = obter_logger("arcee_cli")

# Importação condicional de crewAI
try:
    from arcee_cli.crew.arcee_crew import ArceeCrew
    CREW_AVAILABLE = True
    logger.info("Módulo crewAI carregado com sucesso")
except ImportError:
    CREW_AVAILABLE = False

# Importação da versão simplificada do MCP.run
try:
    from arcee_cli.tools.mcpx_simple import MCPRunClient, configure_mcprun
    MCPRUN_SIMPLE_AVAILABLE = True
    logger.info("Módulo MCPRunClient simplificado disponível")
except ImportError:
    MCPRUN_SIMPLE_AVAILABLE = False
    logger.warning("Módulo MCPRunClient simplificado não disponível")

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

    Comandos para gerenciar as integrações com MCP.run.
    """
)
app.add_typer(mcp_app, name="mcp")

# Cria um grupo de comandos para logs
logs_app = typer.Typer(
    help="""
    📝 Gerenciamento de logs

    Comandos para visualizar e gerenciar os logs do sistema.
    """
)
app.add_typer(logs_app, name="logs")

# Cria um grupo de comandos para crew
crew_app = typer.Typer(
    help="""
    👥 Gerenciamento de tripulações (crews)

    Comandos para gerenciar tripulações de agentes usando CrewAI.
    """
)
app.add_typer(crew_app, name="crew")

# Cria um grupo de comandos para Trello
trello_app = typer.Typer(
    help="""
    📋 Gerenciamento de Trello

    Comandos para gerenciar quadros e cards do Trello.
    """
)
app.add_typer(trello_app, name="trello")

console = Console()

# Provedor global para ser reutilizado em diferentes comandos
_provider = None
_agent = None
_crew = None
_mcp_session_id = None


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
        _crew = ArceeCrew(session_id=_mcp_session_id)
    return _crew


@app.command()
def chat():
    """Inicia um chat com o Arcee AI"""
    logger.info("Iniciando chat com Arcee AI")
    
    # Inicializa o processador do Trello
    try:
        from arcee_cli.tools.trello_nl_processor import TrelloNLProcessor
        trello_processor = TrelloNLProcessor(agent=get_agent())
        TRELLO_NL_AVAILABLE = True
        logger.info("Processador de linguagem natural do Trello carregado")
        
        # Mensagem de boas-vindas com informação sobre o Trello
        welcome_message = "🤖 Chat com Arcee AI\n\n" + \
                         "💡 Você pode usar linguagem natural para interagir com o Trello:\n" + \
                         "   - 'Mostrar listas do Trello'\n" + \
                         "   - 'Criar uma lista chamada Tarefas Importantes'\n" + \
                         "   - 'Mostrar cards da lista Tarefas'\n" + \
                         "   - 'Criar card Estudar Python na lista Tarefas'\n\n" + \
                         "Digite 'sair' para encerrar."
    except Exception as e:
        logger.error(f"Erro ao carregar processador de linguagem natural do Trello: {e}")
        TRELLO_NL_AVAILABLE = False
        trello_processor = None
        
        # Mensagem de boas-vindas padrão
        welcome_message = "🤖 Chat com Arcee AI\n\nDigite 'sair' para encerrar."
    
    print(
        Panel(
            welcome_message,
            title="Arcee AI",
        )
    )

    provider = get_provider()
    messages = []
    
    while True:
        try:
            user_input = Prompt.ask("\nVocê")

            if user_input.lower() == "sair":
                logger.info("Usuário encerrou o chat")
                break

            logger.debug(f"Mensagem do usuário: {user_input}")
            messages.append({"role": "user", "content": user_input})
            
            # Verifica se é um comando do Trello
            trello_response = None
            is_trello_cmd = False
            cmd_type = None
            
            if TRELLO_NL_AVAILABLE and trello_processor:
                is_trello_cmd, cmd_type, cmd_params = trello_processor.detectar_comando(user_input)
                if is_trello_cmd and cmd_type is not None:
                    logger.info(f"Detectado comando do Trello: {cmd_type}")
                    trello_response = trello_processor.processar_comando(cmd_type, cmd_params)
            
            # Se foi processado como comando do Trello e temos uma resposta, exibe a resposta
            if trello_response:
                # Adiciona a resposta ao histórico
                messages.append({"role": "assistant", "content": trello_response})
                print(f"\nAssistente: {trello_response}")
                continue
            
            # Se é sobre Trello mas não é um comando específico ou foi um comando não reconhecido
            if is_trello_cmd and not trello_response:
                # Feedback imediato para o usuário
                print("\nAssistente: 🔍 Processando sua consulta sobre o Trello... aguarde um momento.")
                
                # Criar uma versão modificada da mensagem para o modelo
                # para que ele saiba que é sobre Trello mas não é um comando reconhecido
                trello_context_message = {
                    "role": "system", 
                    "content": "O usuário está perguntando sobre o Trello, mas não usou um comando específico reconhecido. " + 
                              "Responda de forma breve e conversacional sobre o Trello, fazendo perguntas para entender melhor o que o usuário deseja. " +
                              "O Trello é uma ferramenta de gerenciamento de projetos que permite organizar tarefas em quadros, listas e cartões. " +
                              "A implementação atual suporta comandos para gerenciar quadros, listas e cards. " +
                              "\n\nTente descobrir qual aspecto do Trello interessa ao usuário (quadros, listas, cards, etc.) e " +
                              "forneça informações específicas sobre isso, sugerindo comandos relevantes. " +
                              "Por exemplo, se o usuário parece interessado em quadros, sugira 'mostrar quadros', 'criar quadro', etc. " +
                              "\n\nMenções a funcionalidades como checklists, etiquetas, comentários e anexos devem reconhecer que " +
                              "estas são funcionalidades do Trello, mas direcionar o usuário para os comandos atualmente implementados: " +
                              "'mostrar quadros', 'mostrar listas', 'listar listas do quadro com id [ID]', " +
                              "'criar lista', 'criar card', 'criar quadro', 'apagar quadro'."
                }
                
                # Cria uma cópia dos messages para não modificar a lista original
                enhanced_messages = messages.copy()
                enhanced_messages.insert(-1, trello_context_message)  # Insere antes da última mensagem do usuário
                
                # Processa com o contexto adicional
                response = provider.generate_content_chat(enhanced_messages)
            else:
                # Se não é sobre Trello, processa normalmente
                response = provider.generate_content_chat(messages)

            if "error" in response:
                logger.error(f"Erro na resposta: {response['error']}")
                print(f"❌ {response['error']}")
                continue

            # O ArceeProvider retorna a resposta na chave 'text'
            if "text" in response:
                content = response["text"]
                # Adiciona a resposta ao histórico
                messages.append({"role": "assistant", "content": content})
                logger.debug(f"Resposta do assistente: {content}")
                print(f"\nAssistente: {content}")
            else:
                # Fallback para o formato antigo (caso haja alterações futuras)
                logger.warning(f"Formato de resposta não reconhecido: {list(response.keys())}")
                print("⚠️ Formato de resposta não reconhecido")
                print(f"Chaves disponíveis: {list(response.keys())}")

        except KeyboardInterrupt:
            logger.info("Chat interrompido pelo usuário (KeyboardInterrupt)")
            break
        except Exception as e:
            logger.exception(f"Erro no chat: {str(e)}")
            print(f"❌ Erro: {str(e)}")
            import traceback
            traceback.print_exc()
            break

    logger.info("Chat encerrado")
    print("\nAté logo! 👋")


@app.command()
def configure(
    api_key: str = typer.Option(None, help="Chave da API do Arcee"),
    org: str = typer.Option(None, help="Organização do Arcee"),
):
    """Configura a CLI do Arcee"""
    logger.info("Iniciando configuração da CLI")
    config_setup(api_key=api_key, org=org)
    logger.info("Configuração da CLI concluída")


@mcp_app.command("configurar")
def configurar_mcp(
    session_id: Optional[str] = typer.Option(None, help="ID de sessão MCP.run existente"),
):
    """Configura a integração com MCP.run"""
    global _mcp_session_id
    
    # Verifica se temos a implementação simplificada disponível
    if MCPRUN_SIMPLE_AVAILABLE:
        print("🔄 Usando implementação simplificada do MCP.run...")
        try:
            # Configura usando a implementação simplificada
            new_session_id = configure_mcprun(session_id)
            
            if new_session_id:
                _mcp_session_id = new_session_id
                print(f"✅ ID de sessão MCP.run configurado: {new_session_id}")
                
                # Salvar no arquivo de configuração para persistência
                config_file = os.path.expanduser("~/.arcee/config.json")
                try:
                    # Carrega configuração existente
                    config = {}
                    if os.path.exists(config_file):
                        with open(config_file, "r", encoding="utf-8") as f:
                            config = json.load(f)
                            
                    # Atualiza com novo ID de sessão
                    config["mcp_session_id"] = new_session_id
                    
                    # Salva a configuração
                    with open(config_file, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=2)
                        
                    logger.info(f"ID de sessão MCP.run salvo: {new_session_id}")
                except Exception as e:
                    logger.error(f"Erro ao salvar ID de sessão MCP.run: {e}")
                    print(f"⚠️ Erro ao salvar configuração: {e}")
                
                # Teste a conexão listando ferramentas
                client = MCPRunClient(session_id=new_session_id)
                tools = client.get_tools()
                print(f"ℹ️ Encontradas {len(tools)} ferramentas disponíveis")
                
                return
            else:
                print("❌ Não foi possível configurar o MCP.run")
                print("💡 Verifique os logs para mais detalhes")
                return
        except Exception as e:
            logger.exception(f"Erro ao configurar MCP.run simplificado: {e}")
            print(f"❌ Erro ao configurar MCP.run: {e}")
            return
    
    # Caso não tenha a implementação simplificada
    print("❌ Módulo MCP.run não está disponível")
    print("💡 Verifique a instalação do pacote simplificado")


@mcp_app.command("listar")
def listar_ferramentas_mcp():
    """Lista todas as ferramentas disponíveis no MCP.run"""
    # Verifica se temos a implementação simplificada disponível
    if MCPRUN_SIMPLE_AVAILABLE:
        global _mcp_session_id
        
        # Carrega ID de sessão se não estiver definido
        if not _mcp_session_id:
            config_file = os.path.expanduser("~/.arcee/config.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        _mcp_session_id = config.get("mcp_session_id")
                except Exception as e:
                    logger.error(f"Erro ao carregar ID de sessão MCP.run: {e}")
        
        # Verifica se temos um ID de sessão
        if not _mcp_session_id:
            print("❌ ID de sessão MCP.run não configurado")
            print("💡 Execute primeiro: arcee mcp configurar")
            return
            
        # Obtém as ferramentas com a implementação simplificada
        print("🔍 Obtendo lista de ferramentas disponíveis...")
        try:
            client = MCPRunClient(session_id=_mcp_session_id)
            tools = client.get_tools()
            
            if not tools:
                print("ℹ️ Nenhuma ferramenta MCP.run disponível")
                return
                
            # Cria a tabela
            tabela = Table(title="🔌 Ferramentas MCP.run")
            tabela.add_column("Nome", style="cyan")
            tabela.add_column("Descrição", style="green")
            
            # Adiciona as ferramentas à tabela
            for tool in tools:
                tabela.add_row(tool["name"], tool["description"])
                
            # Exibe a tabela
            console.print(tabela)
            
        except Exception as e:
            logger.exception(f"Erro ao listar ferramentas MCP.run: {e}")
            print(f"❌ Erro ao listar ferramentas MCP.run: {e}")
        return
    
    # Caso não tenha a implementação simplificada
    print("❌ Módulo MCP.run não está disponível")
    print("💡 Verifique a instalação do pacote simplificado")


@mcp_app.command("executar")
def executar_ferramenta(
    nome: str = typer.Argument(..., help="Nome da ferramenta para executar"),
    params: str = typer.Option(None, help="Parâmetros da ferramenta em formato JSON"),
):
    """Executa uma ferramenta MCP.run específica"""
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCP.run não está disponível")
        print("💡 Verifique a instalação do pacote simplificado")
        return
        
    global _mcp_session_id
    
    # Carrega ID de sessão se não estiver definido
    if not _mcp_session_id:
        config_file = os.path.expanduser("~/.arcee/config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    _mcp_session_id = config.get("mcp_session_id")
            except Exception as e:
                logger.error(f"Erro ao carregar ID de sessão MCP.run: {e}")
    
    # Verifica se temos um ID de sessão
    if not _mcp_session_id:
        print("❌ ID de sessão MCP.run não configurado")
        print("💡 Execute primeiro: arcee mcp configurar")
        return
        
    # Processa os parâmetros
    try:
        params_dict = {}
        if params:
            params_dict = json.loads(params)
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        print(f"❌ Erro nos parâmetros JSON: {e}")
        return
        
    # Executa a ferramenta
    print(f"🚀 Executando ferramenta '{nome}'...")
    try:
        client = MCPRunClient(session_id=_mcp_session_id)
        result = client.run_tool(nome, params_dict)
        
        if "error" in result:
            print(f"❌ Erro ao executar ferramenta: {result['error']}")
            if "raw_output" in result:
                print("Saída original:")
                print(result["raw_output"])
        else:
            print("✅ Resultado:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    except Exception as e:
        logger.exception(f"Erro ao executar ferramenta: {e}")
        print(f"❌ Erro ao executar ferramenta: {e}")


@crew_app.command("configurar")
def configurar_crew(
    config_dir: str = typer.Option(
        os.path.expanduser("~/.arcee/config"),
        help="Diretório para arquivos de configuração"
    ),
    agents_file: str = typer.Option(
        "agents.yaml",
        help="Nome do arquivo de configuração de agentes"
    ),
    tasks_file: str = typer.Option(
        "tasks.yaml",
        help="Nome do arquivo de configuração de tarefas"
    )
):
    """Configura arquivos para tripulação CrewAI"""
    if not CREW_AVAILABLE:
        print("❌ Módulo CrewAI não está disponível. Instale: pip install crewai")
        print("💡 Você também pode instalar todas as dependências: pip install -r requirements.txt")
        return
        
    # Cria diretório se não existir
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
        logger.info(f"Diretório de configuração criado: {config_dir}")
    
    # Inicializa a tripulação para criar os arquivos de configuração padrão
    try:
        crew = ArceeCrew(
            config_dir=config_dir,
            agents_file=agents_file,
            tasks_file=tasks_file,
            session_id=_mcp_session_id
        )
        
        agents_path = os.path.join(config_dir, agents_file)
        tasks_path = os.path.join(config_dir, tasks_file)
        
        print(f"✅ Configuração da tripulação concluída")
        print(f"📂 Diretório de configuração: {config_dir}")
        print(f"📄 Arquivo de agentes: {agents_path}")
        print(f"📄 Arquivo de tarefas: {tasks_path}")
        
    except Exception as e:
        logger.exception(f"Erro ao configurar tripulação: {e}")
        print(f"❌ Erro ao configurar tripulação: {e}")


@crew_app.command("executar")
def executar_crew(
    config_dir: str = typer.Option(
        os.path.expanduser("~/.arcee/config"),
        help="Diretório para arquivos de configuração"
    ),
    agents_file: str = typer.Option(
        "agents.yaml",
        help="Nome do arquivo de configuração de agentes"
    ),
    tasks_file: str = typer.Option(
        "tasks.yaml",
        help="Nome do arquivo de configuração de tarefas"
    ),
    process: str = typer.Option(
        "sequential",
        help="Tipo de processo (sequential ou hierarchical)"
    )
):
    """Executa a tripulação CrewAI com as configurações especificadas"""
    if not CREW_AVAILABLE:
        print("❌ Módulo CrewAI não está disponível. Instale: pip install crewai")
        print("💡 Você também pode instalar todas as dependências: pip install -r requirements.txt")
        return
        
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCP.run não está disponível.")
        print("💡 Verifique a instalação do pacote simplificado")
        return
        
    # Carrega ID de sessão se não estiver definido
    global _mcp_session_id
    if not _mcp_session_id:
        config_file = os.path.expanduser("~/.arcee/config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    _mcp_session_id = config.get("mcp_session_id")
            except Exception as e:
                logger.error(f"Erro ao carregar ID de sessão MCP.run: {e}")
    
    # Verifica se temos um ID de sessão
    if not _mcp_session_id:
        print("❌ ID de sessão MCP.run não configurado")
        print("💡 Execute primeiro: arcee mcp configurar")
        return
        
    # Verifica se os arquivos de configuração existem
    agents_path = os.path.join(config_dir, agents_file)
    tasks_path = os.path.join(config_dir, tasks_file)
    
    if not os.path.exists(agents_path):
        print(f"❌ Arquivo de agentes não encontrado: {agents_path}")
        print("💡 Execute primeiro: arcee crew configurar")
        return
        
    if not os.path.exists(tasks_path):
        print(f"❌ Arquivo de tarefas não encontrado: {tasks_path}")
        print("💡 Execute primeiro: arcee crew configurar")
        return
    
    # Inicializa e executa a tripulação
    try:
        print("🚀 Inicializando tripulação CrewAI...")
        crew = ArceeCrew(
            config_dir=config_dir,
            agents_file=agents_file,
            tasks_file=tasks_file,
            session_id=_mcp_session_id,
            process=process
        )
        
        print("⏳ Criando agentes e tarefas...")
        crew.create_agents()
        crew.create_tasks()
        crew.create_crew()
        
        print("🔄 Executando tripulação...")
        resultado = crew.run()
        
        print("\n✅ Execução concluída!\n")
        print(Panel(
            resultado,
            title="Resultado",
            border_style="green"
        ))
        
    except Exception as e:
        logger.exception(f"Erro ao executar tripulação: {e}")
        print(f"❌ Erro ao executar tripulação: {e}")


@logs_app.command("listar")
def listar_logs():
    """Lista os arquivos de log disponíveis"""
    logger.info("Listando arquivos de log")
    try:
        # Verifica se o diretório de logs existe
        if not os.path.exists(LOG_DIR):
            print(f"❌ Diretório de logs não encontrado: {LOG_DIR}")
            return
            
        # Lista arquivos de log
        logs = [f for f in os.listdir(LOG_DIR) if f.endswith('.log')]
        
        if not logs:
            print("ℹ️ Nenhum arquivo de log encontrado.")
            return
            
        # Cria a tabela
        tabela = Table(title="📝 Arquivos de Log")
        tabela.add_column("Nome", style="cyan")
        tabela.add_column("Tamanho", style="green")
        tabela.add_column("Data de Modificação", style="yellow")
        
        # Adiciona os arquivos à tabela
        for log_file in logs:
            path = os.path.join(LOG_DIR, log_file)
            size = os.path.getsize(path)
            size_str = f"{size / 1024:.2f} KB" if size > 1024 else f"{size} bytes"
            mtime = os.path.getmtime(path)
            import datetime
            mtime_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            tabela.add_row(log_file, size_str, mtime_str)
            
        # Exibe a tabela
        console.print(tabela)
        
    except Exception as e:
        logger.exception(f"Erro ao listar logs: {e}")
        print(f"❌ Erro ao listar logs: {e}")


@logs_app.command("ver")
def ver_log(
    linhas: int = typer.Option(50, help="Número de linhas para exibir"),
    arquivo: str = typer.Option("arcee.log", help="Nome do arquivo de log para exibir"),
):
    """Exibe o conteúdo do arquivo de log"""
    logger.info(f"Exibindo {linhas} linhas do arquivo de log {arquivo}")
    try:
        # Constrói o caminho do arquivo
        path = os.path.join(LOG_DIR, arquivo)
        
        # Verifica se o arquivo existe
        if not os.path.exists(path):
            print(f"❌ Arquivo de log não encontrado: {path}")
            return
            
        # Lê as últimas linhas do arquivo
        with open(path, "r", encoding="utf-8") as f:
            # Lê todas as linhas do arquivo
            all_lines = f.readlines()
            
            # Obtém as últimas 'linhas' linhas
            last_lines = all_lines[-linhas:] if len(all_lines) > linhas else all_lines
            
            # Junta as linhas em uma string
            content = "".join(last_lines)
            
            # Exibe o conteúdo
            syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"📝 {arquivo} (últimas {len(last_lines)} de {len(all_lines)} linhas)"))
            
    except Exception as e:
        logger.exception(f"Erro ao exibir log: {e}")
        print(f"❌ Erro ao exibir log: {e}")


@logs_app.command("limpar")
def limpar_logs(
    confirmar: bool = typer.Option(False, "--sim", help="Confirma a operação sem prompt"),
):
    """Limpa os arquivos de log"""
    logger.info("Solicitação para limpar logs")
    try:
        # Verifica se o diretório de logs existe
        if not os.path.exists(LOG_DIR):
            print(f"ℹ️ Diretório de logs não encontrado: {LOG_DIR}")
            return
            
        # Lista arquivos de log
        logs = [f for f in os.listdir(LOG_DIR) if f.endswith('.log')]
        
        if not logs:
            print("ℹ️ Nenhum arquivo de log encontrado para limpar.")
            return
            
        # Confirma a operação
        if not confirmar:
            confirmacao = Prompt.ask(
                f"⚠️ Deseja realmente limpar {len(logs)} arquivos de log?",
                choices=["s", "n"],
                default="n"
            )
            
            if confirmacao.lower() != "s":
                print("❌ Operação cancelada pelo usuário.")
                return
                
        # Limpa os arquivos
        for log_file in logs:
            path = os.path.join(LOG_DIR, log_file)
            try:
                # Abre o arquivo em modo de escrita para truncá-lo
                with open(path, "w") as f:
                    pass
                logger.info(f"Arquivo de log limpo: {log_file}")
            except Exception as e:
                logger.error(f"Erro ao limpar arquivo {log_file}: {e}")
                print(f"⚠️ Erro ao limpar arquivo {log_file}: {e}")
                
        print(f"✅ {len(logs)} arquivos de log foram limpos com sucesso.")
        
    except Exception as e:
        logger.exception(f"Erro ao limpar logs: {e}")
        print(f"❌ Erro ao limpar logs: {e}")


@logs_app.command("nivel")
def definir_nivel(
    nivel: str = typer.Argument(
        ..., 
        help="Nível de log (debug, info, warning, error, critical)"
    ),
    sessao_atual: bool = typer.Option(
        True, 
        help="Aplica o nível apenas à sessão atual (não permanente)"
    ),
):
    """Define o nível de log para a aplicação"""
    logger.info(f"Solicitação para definir nível de log para: {nivel}")
    
    # Mapeia strings para níveis do logging
    niveis = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    
    if nivel.lower() not in niveis:
        print(f"❌ Nível de log inválido: {nivel}")
        print(f"ℹ️ Níveis válidos: {', '.join(niveis.keys())}")
        return
        
    nivel_log = niveis[nivel.lower()]
    
    # Define o nível do logger raiz
    logging.getLogger().setLevel(nivel_log)
    
    # Se solicitado para ser permanente, altera as configurações permanentes
    # Esta parte precisaria de uma implementação para salvar as configurações
    
    print(f"✅ Nível de log definido para: {nivel.upper()}")
    
    if sessao_atual:
        print("ℹ️ Esta configuração se aplica apenas à sessão atual.")


@logs_app.command("teste")
def testar_logs():
    """Gera mensagens de log de teste em todos os níveis"""
    logger.info("Executando teste de logging em todos os níveis")
    
    print("🧪 Gerando mensagens de teste em todos os níveis de log...")
    
    # Gera mensagens de log em todos os níveis
    logger.debug("Esta é uma mensagem de DEBUG para teste")
    logger.info("Esta é uma mensagem de INFO para teste")
    logger.warning("Esta é uma mensagem de WARNING para teste") 
    logger.error("Esta é uma mensagem de ERROR para teste")
    logger.critical("Esta é uma mensagem de CRITICAL para teste")
    
    try:
        # Simula um erro para demonstrar o logger.exception
        1 / 0
    except Exception as e:
        logger.exception("Esta é uma demonstração de logger.exception")
    
    print("✅ Mensagens de teste geradas com sucesso")
    print("💡 Use 'arcee logs ver' para visualizar as mensagens no arquivo de log")


@trello_app.command("iniciar")
def iniciar_servidor_trello(
    background: bool = typer.Option(False, "--background", "-b", help="Iniciar em segundo plano"),
    board_id: Optional[str] = typer.Option(None, "--board", help="ID do quadro Trello a ser usado")
):
    """Inicia o servidor Trello localmente"""
    logger.info(f"Iniciando servidor Trello (background={background}, board_id={board_id})")
    
    # Determina o diretório raiz do projeto
    projeto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_dir = os.path.join(projeto_dir, "arcee_cli", "scripts")
    
    if background:
        script_path = os.path.join(scripts_dir, "start_trello_server_background.sh")
    else:
        script_path = os.path.join(scripts_dir, "start_trello_server.sh")
    
    print(f"🚀 Iniciando servidor Trello {'em segundo plano' if background else ''}...")
    
    try:
        # Adiciona o board_id como argumento se fornecido
        cmd = ["bash", script_path]
        if board_id:
            cmd.append(board_id)
            print(f"📋 Usando quadro com ID: {board_id}")
            
        if background:
            # Em segundo plano, apenas executa o script
            subprocess.run(
                cmd,
                check=True,
                text=True
            )
        else:
            # Em primeiro plano, executa o processo diretamente
            os.execv("/bin/bash", ["bash"] + cmd[1:])
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor Trello: {e}")
        logger.error(f"Erro ao iniciar servidor Trello: {e}")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor Trello: {e}")
        logger.exception(f"Erro ao iniciar servidor Trello: {e}")

@trello_app.command("listar-listas")
def listar_listas_trello():
    """Lista todas as listas do quadro Trello"""
    logger.info("Listando listas do Trello")
    
    import requests
    
    # Verifica as credenciais
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    board_id = os.getenv("TRELLO_BOARD_ID")
    
    if not api_key or not token:
        print("❌ Erro: Credenciais do Trello não encontradas")
        print("Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos no arquivo .env")
        return
        
    if not board_id:
        print("❌ Erro: ID do quadro Trello não encontrado")
        print("Verifique se TRELLO_BOARD_ID está definido no arquivo .env")
        return
    
    try:
        # Parâmetros da requisição
        params = {
            "key": api_key,
            "token": token
        }
        
        print(f"🔄 Obtendo listas do quadro {board_id}...")
        
        # Faz a requisição para obter as listas
        response = requests.get(f"https://api.trello.com/1/boards/{board_id}/lists", params=params)
        response.raise_for_status()
        
        listas = response.json()
        
        if not listas:
            print("ℹ️ Nenhuma lista encontrada neste quadro.")
            return
            
        # Exibe as listas em uma tabela
        table = Table(title="📋 Listas do Trello")
        table.add_column("ID", style="cyan")
        table.add_column("Nome", style="green")
        table.add_column("Posição", style="magenta")
        
        for lista in listas:
            table.add_row(
                lista.get("id", "N/A"),
                lista.get("name", "N/A"),
                str(lista.get("pos", 0))
            )
            
        console.print(table)
        
        # Retorna as listas para possível uso em outros comandos
        return listas
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao listar listas: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Resposta: {e.response.text}")
        logger.exception(f"Erro ao listar listas do Trello: {e}")

@trello_app.command("listar-cards")
def listar_cards_trello(
    lista_id: Optional[str] = typer.Argument(None, help="ID da lista para filtrar os cards")
):
    """Lista todos os cards do quadro ou de uma lista específica"""
    logger.info(f"Listando cards do Trello (lista_id={lista_id})")
    
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCPRunClient não disponível")
        return
    
    # Usa o agente para obter as cards
    agent = get_agent()
    try:
        # Se não tem ID de lista, exibe os cards de todas as listas
        if not lista_id:
            # Primeiro obtém as listas
            listas_response = agent.run_tool("get_lists", {"random_string": "dummy"})
            
            if "error" in listas_response:
                print(f"❌ Erro: {listas_response['error']}")
                return
                
            all_cards = []
            
            # Para cada lista, obtém os cards
            for lista in listas_response.get("lists", []):
                lista_id = lista.get("id")
                lista_nome = lista.get("name")
                
                cards_response = agent.run_tool("get_cards_by_list_id", {"listId": lista_id})
                
                if "error" not in cards_response:
                    for card in cards_response.get("cards", []):
                        card["listName"] = lista_nome
                        all_cards.append(card)
            
            # Exibe todos os cards em uma tabela
            table = Table(title="🗂️ Todos os Cards do Trello")
            table.add_column("ID", style="cyan")
            table.add_column("Lista", style="blue")
            table.add_column("Nome", style="green")
            table.add_column("Descrição", style="magenta")
            
            for card in all_cards:
                table.add_row(
                    card.get("id", "N/A"),
                    card.get("listName", "N/A"),
                    card.get("name", "N/A"),
                    card.get("desc", "")[:30] + ("..." if len(card.get("desc", "")) > 30 else "")
                )
                
            console.print(table)
        else:
            # Exibe os cards de uma lista específica
            response = agent.run_tool("get_cards_by_list_id", {"listId": lista_id})
            
            if "error" in response:
                print(f"❌ Erro: {response['error']}")
                return
                
            # Exibe os cards em uma tabela
            table = Table(title=f"🗂️ Cards da Lista {lista_id}")
            table.add_column("ID", style="cyan")
            table.add_column("Nome", style="green")
            table.add_column("Descrição", style="magenta")
            
            for card in response.get("cards", []):
                table.add_row(
                    card.get("id", "N/A"),
                    card.get("name", "N/A"),
                    card.get("desc", "")[:50] + ("..." if len(card.get("desc", "")) > 50 else "")
                )
                
            console.print(table)
    except Exception as e:
        print(f"❌ Erro ao listar cards: {e}")
        logger.exception(f"Erro ao listar cards do Trello: {e}")

@trello_app.command("criar-lista")
def criar_lista_trello(
    nome: str = typer.Argument(..., help="Nome da nova lista")
):
    """Cria uma nova lista no quadro Trello"""
    logger.info(f"Criando lista no Trello: {nome}")
    
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCPRunClient não disponível")
        return
    
    # Usa o agente para criar a lista
    agent = get_agent()
    try:
        response = agent.run_tool("add_list_to_board", {"name": nome})
        
        if "error" in response:
            print(f"❌ Erro: {response['error']}")
            return
            
        print(f"✅ Lista '{nome}' criada com sucesso!")
        print(f"ID da lista: {response.get('id')}")
    except Exception as e:
        print(f"❌ Erro ao criar lista: {e}")
        logger.exception(f"Erro ao criar lista no Trello: {e}")

@trello_app.command("criar-card")
def criar_card_trello(
    lista_id: str = typer.Argument(..., help="ID da lista onde o card será criado"),
    nome: str = typer.Argument(..., help="Nome do card"),
    descricao: str = typer.Option("", "--desc", "-d", help="Descrição do card"),
    data_vencimento: str = typer.Option(None, "--due", help="Data de vencimento (formato ISO 8601, ex: 2023-12-31T23:59:59Z)")
):
    """Cria um novo card em uma lista do Trello"""
    logger.info(f"Criando card no Trello: {nome} (lista_id={lista_id})")
    
    import requests
    
    # Verifica as credenciais
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    
    if not api_key or not token:
        print("❌ Erro: Credenciais do Trello não encontradas")
        print("Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos no arquivo .env")
        return
    
    try:
        # Parâmetros da requisição para criar card
        params = {
            "key": api_key,
            "token": token,
            "idList": lista_id,
            "name": nome,
            "desc": descricao
        }
        
        if data_vencimento:
            params["due"] = data_vencimento
        
        print(f"🔄 Criando card '{nome}' na lista {lista_id}...")
        
        # Faz a requisição para criar o card
        response = requests.post("https://api.trello.com/1/cards", params=params)
        response.raise_for_status()
        
        card_data = response.json()
        print(f"✅ Card criado com sucesso!")
        print(f"ID do card: {card_data['id']}")
        print(f"URL do card: {card_data['url']}")
        
        return card_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao criar card: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Resposta: {e.response.text}")
        logger.exception(f"Erro ao criar card no Trello: {e}")

@trello_app.command("arquivar-card")
def arquivar_card_trello(
    card_id: str = typer.Argument(..., help="ID do card a ser arquivado")
):
    """Arquiva um card do Trello"""
    logger.info(f"Arquivando card do Trello: {card_id}")
    
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCPRunClient não disponível")
        return
    
    # Usa o agente para arquivar o card
    agent = get_agent()
    try:
        response = agent.run_tool("archive_card", {"cardId": card_id})
        
        if "error" in response:
            print(f"❌ Erro: {response['error']}")
            return
            
        print(f"✅ Card {card_id} arquivado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao arquivar card: {e}")
        logger.exception(f"Erro ao arquivar card do Trello: {e}")

@trello_app.command("atividade")
def listar_atividade_trello(
    limite: int = typer.Option(10, "--limite", "-l", help="Número de atividades a serem exibidas")
):
    """Lista as atividades recentes no quadro Trello"""
    logger.info(f"Listando atividades do Trello (limite={limite})")
    
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCPRunClient não disponível")
        return
    
    # Usa o agente para obter as atividades
    agent = get_agent()
    try:
        response = agent.run_tool("get_recent_activity", {"limit": limite})
        
        if "error" in response:
            print(f"❌ Erro: {response['error']}")
            return
            
        # Exibe as atividades em uma tabela
        table = Table(title="🔄 Atividades Recentes do Trello")
        table.add_column("Data", style="cyan")
        table.add_column("Usuário", style="blue")
        table.add_column("Ação", style="green")
        
        for atividade in response.get("activities", []):
            date_str = atividade.get("date", "")
            # Formata a data se disponível
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    date_formatted = date_obj.strftime("%d/%m/%Y %H:%M")
                except:
                    date_formatted = date_str
            else:
                date_formatted = "N/A"
                
            table.add_row(
                date_formatted,
                atividade.get("memberCreator", {}).get("fullName", "N/A"),
                atividade.get("data", {}).get("text", atividade.get("type", "N/A"))
            )
            
        console.print(table)
    except Exception as e:
        print(f"❌ Erro ao listar atividades: {e}")
        logger.exception(f"Erro ao listar atividades do Trello: {e}")

@trello_app.command("meus-cards")
def listar_meus_cards_trello():
    """Lista todos os cards atribuídos a você"""
    logger.info("Listando meus cards do Trello")
    
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCPRunClient não disponível")
        return
    
    # Usa o agente para obter os cards
    agent = get_agent()
    try:
        response = agent.run_tool("get_my_cards", {"random_string": "dummy"})
        
        if "error" in response:
            print(f"❌ Erro: {response['error']}")
            return
            
        # Exibe os cards em uma tabela
        table = Table(title="🗂️ Meus Cards do Trello")
        table.add_column("ID", style="cyan")
        table.add_column("Lista", style="blue")
        table.add_column("Nome", style="green")
        table.add_column("Data Vencimento", style="magenta")
        
        for card in response.get("cards", []):
            due_date = card.get("due", "")
            # Formata a data se disponível
            if due_date:
                try:
                    date_obj = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    due_formatted = date_obj.strftime("%d/%m/%Y")
                except:
                    due_formatted = due_date
            else:
                due_formatted = "N/A"
                
            table.add_row(
                card.get("id", "N/A"),
                card.get("list", {}).get("name", "N/A"),
                card.get("name", "N/A"),
                due_formatted
            )
            
        console.print(table)
    except Exception as e:
        print(f"❌ Erro ao listar meus cards: {e}")
        logger.exception(f"Erro ao listar meus cards do Trello: {e}")

@trello_app.command("atualizar-card")
def atualizar_card_trello(
    card_id: str = typer.Argument(..., help="ID do card a ser atualizado"),
    nome: str = typer.Option(None, "--nome", "-n", help="Novo nome para o card"),
    descricao: str = typer.Option(None, "--desc", "-d", help="Nova descrição para o card"),
    data_vencimento: str = typer.Option(None, "--due", help="Nova data de vencimento (formato ISO 8601, ex: 2023-12-31T23:59:59Z)")
):
    """Atualiza os detalhes de um card existente no Trello"""
    logger.info(f"Atualizando card no Trello: {card_id}")
    
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCPRunClient não disponível")
        return
    
    if not any([nome, descricao, data_vencimento]):
        print("❌ Você precisa fornecer pelo menos um campo para atualizar (nome, descrição ou data)")
        return
    
    # Usa o agente para atualizar o card
    agent = get_agent()
    try:
        params = {"cardId": card_id}
        
        if nome:
            params["name"] = nome
        
        if descricao:
            params["description"] = descricao
            
        if data_vencimento:
            params["dueDate"] = data_vencimento
            
        response = agent.run_tool("update_card_details", params)
        
        if "error" in response:
            print(f"❌ Erro: {response['error']}")
            return
            
        print(f"✅ Card {card_id} atualizado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao atualizar card: {e}")
        logger.exception(f"Erro ao atualizar card no Trello: {e}")

@trello_app.command("arquivar-lista")
def arquivar_lista_trello(
    lista_id: str = typer.Argument(..., help="ID da lista a ser arquivada")
):
    """Arquiva uma lista do Trello"""
    logger.info(f"Arquivando lista do Trello: {lista_id}")
    
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Módulo MCPRunClient não disponível")
        return
    
    # Usa o agente para arquivar a lista
    agent = get_agent()
    try:
        response = agent.run_tool("archive_list", {"listId": lista_id})
        
        if "error" in response:
            print(f"❌ Erro: {response['error']}")
            return
            
        print(f"✅ Lista {lista_id} arquivada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao arquivar lista: {e}")
        logger.exception(f"Erro ao arquivar lista do Trello: {e}")

@trello_app.command("criar-quadro")
def criar_quadro_trello(
    nome: str = typer.Argument(..., help="Nome do novo quadro"),
    descricao: str = typer.Option(None, "--desc", "-d", help="Descrição do quadro"),
    listas_padrao: bool = typer.Option(True, "--listas-padrao/--sem-listas", help="Criar listas padrão (A Fazer, Em Andamento, Concluído)")
):
    """Cria um novo quadro no Trello"""
    logger.info(f"Criando quadro no Trello: {nome}")
    
    # Verifica as credenciais
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    
    if not api_key or not token:
        print("❌ Erro: Credenciais do Trello não encontradas")
        print("Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos no arquivo .env")
        return
    
    try:
        # Parâmetros da requisição para criar quadro
        params = {
            "key": api_key,
            "token": token,
            "name": nome,
            "defaultLists": "false"  # Não criar listas padrão automaticamente
        }
        
        if descricao:
            params["desc"] = descricao
        
        print(f"🔄 Criando quadro '{nome}'...")
        
        # Faz a requisição para criar o quadro
        response = requests.post("https://api.trello.com/1/boards/", params=params)
        response.raise_for_status()
        
        board_data = response.json()
        print(f"✅ Quadro criado com sucesso!")
        print(f"ID do quadro: {board_data['id']}")
        print(f"URL do quadro: {board_data['url']}")
        
        board_id = board_data['id']
        
        # Cria listas padrão se solicitado
        if listas_padrao:
            print("\nCriando listas padrão...")
            listas = ["A Fazer", "Em Andamento", "Concluído"]
            
            for lista_nome in listas:
                lista_params = {
                    "key": api_key,
                    "token": token,
                    "name": lista_nome,
                    "idBoard": board_id
                }
                
                print(f"🔄 Criando lista '{lista_nome}'...")
                lista_response = requests.post("https://api.trello.com/1/lists", params=lista_params)
                lista_response.raise_for_status()
                
                lista_data = lista_response.json()
                print(f"✅ Lista '{lista_nome}' criada com sucesso!")
                print(f"ID da lista: {lista_data['id']}")
        
        # Pergunta se quer utilizar este quadro como padrão
        usar_como_padrao = typer.confirm("\nDeseja utilizar este quadro como padrão?", default=True)
        
        if usar_como_padrao:
            # Atualiza os arquivos .env com o novo ID do quadro
            update_env_files(board_id, nome)
            print(f"\n✅ Arquivos .env atualizados com o novo ID do quadro: {board_id}")
            print("Para usar este quadro, reinicie o servidor Trello com o comando:")
            print("  arcee trello iniciar --background")
        else:
            print(f"\nPara usar este quadro posteriormente, você pode iniciar o servidor com:")
            print(f"  arcee trello iniciar --board {board_id}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao criar quadro: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Resposta: {e.response.text}")

def update_env_files(board_id, board_name):
    """Atualiza os arquivos .env com o novo ID do quadro"""
    # Caminho para o arquivo .env principal
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    
    # Caminho para o arquivo .env do servidor Trello
    trello_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp-server-trello", ".env")
    
    # Atualiza o arquivo .env principal
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Substitui o ID do quadro
        content = re.sub(r"TRELLO_BOARD_ID=.*", f"TRELLO_BOARD_ID={board_id}", content)
        content = re.sub(r"TRELLO_BOARD_NAME=.*", f"TRELLO_BOARD_NAME={board_name}", content)
        
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    # Atualiza o arquivo .env do servidor Trello
    if os.path.exists(trello_env_path):
        with open(trello_env_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Substitui o ID do quadro
        content = re.sub(r"TRELLO_BOARD_ID=.*", f"TRELLO_BOARD_ID={board_id}", content)
        
        with open(trello_env_path, "w", encoding="utf-8") as f:
            f.write(content)

@trello_app.command("apagar-quadro")
def apagar_quadro_trello(
    quadro_id_ou_url: str = typer.Argument(..., help="ID do quadro ou URL completa do Trello"),
    confirmar: bool = typer.Option(False, "--sim", "-s", help="Confirmar exclusão sem perguntar")
):
    """Apaga um quadro do Trello permanentemente (cuidado: esta ação não pode ser desfeita)"""
    logger.info(f"Tentando apagar quadro do Trello: {quadro_id_ou_url}")
    
    import requests
    import re
    
    # Verifica se é uma URL ou um ID direto
    if quadro_id_ou_url.startswith("http"):
        # Extrai o ID da URL
        match = re.search(r'trello\.com/b/([^/]+)', quadro_id_ou_url)
        if match:
            quadro_id = match.group(1)
        else:
            print("❌ URL inválida. Formato esperado: https://trello.com/b/BOARD_ID/...")
            return
    else:
        quadro_id = quadro_id_ou_url
    
    # Verifica as credenciais
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    
    if not api_key or not token:
        print("❌ Erro: Credenciais do Trello não encontradas")
        print("Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos no arquivo .env")
        return
    
    # Obtém informações do quadro para mostrar ao usuário
    try:
        info_params = {
            "key": api_key,
            "token": token
        }
        
        # Verifica se o quadro existe e obtém informações
        info_response = requests.get(f"https://api.trello.com/1/boards/{quadro_id}", params=info_params)
        info_response.raise_for_status()
        
        board_info = info_response.json()
        board_name = board_info.get('name', 'Quadro sem nome')
        
        print(f"📋 Quadro encontrado: {board_name} (ID: {quadro_id})")
        
        # Confirma a exclusão
        if not confirmar:
            confirmacao = typer.confirm(f"⚠️ ATENÇÃO: Tem certeza que deseja APAGAR PERMANENTEMENTE o quadro '{board_name}'?")
            if not confirmacao:
                print("Operação cancelada pelo usuário.")
                return
        
        # Parâmetros da requisição para apagar o quadro
        params = {
            "key": api_key,
            "token": token
        }
        
        print(f"🔄 Apagando quadro '{board_name}'...")
        
        # Faz a requisição para apagar o quadro
        response = requests.delete(f"https://api.trello.com/1/boards/{quadro_id}", params=params)
        response.raise_for_status()
        
        print(f"✅ Quadro '{board_name}' apagado com sucesso!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao apagar quadro: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Resposta: {e.response.text}")
        logger.exception(f"Erro ao apagar quadro do Trello: {e}")

@trello_app.command("listar-quadros")
def listar_quadros_trello():
    """Lista todos os quadros do usuário no Trello"""
    try:
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            typer.echo("Erro: TRELLO_API_KEY e TRELLO_TOKEN devem estar definidos como variáveis de ambiente")
            raise typer.Exit(code=1)
        
        url = "https://api.trello.com/1/members/me/boards"
        query = {
            'key': api_key,
            'token': token,
            'fields': 'name,url'
        }
        
        response = requests.get(url, params=query)
        
        if response.status_code != 200:
            typer.echo(f"Erro ao obter quadros do Trello: {response.status_code}")
            raise typer.Exit(code=1)
            
        quadros = response.json()
        
        if not quadros:
            typer.echo("Nenhum quadro encontrado.")
            return
            
        typer.echo("Quadros do Trello:")
        for quadro in quadros:
            typer.echo(f"- {quadro['name']} (ID: {quadro['id']}, URL: {quadro['url']})")
            
    except Exception as e:
        typer.echo(f"Erro ao listar quadros do Trello: {str(e)}")
        raise typer.Exit(code=1)

@trello_app.command("buscar-card")
def buscar_card_trello(
    termo: str = typer.Argument(..., help="Nome ou parte do nome do card a ser localizado"),
    quadro_id: Optional[str] = typer.Option(None, "--quadro", "-q", help="ID do quadro específico para buscar (opcional)")
):
    """Busca um card pelo nome e mostra em qual lista ele está localizado"""
    try:
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            typer.echo("Erro: TRELLO_API_KEY e TRELLO_TOKEN devem estar definidos como variáveis de ambiente")
            raise typer.Exit(code=1)
        
        # Se o quadro_id não foi especificado, busca em todos os quadros
        if not quadro_id:
            # Obter todos os quadros do usuário
            url = "https://api.trello.com/1/members/me/boards"
            query = {
                'key': api_key,
                'token': token,
                'fields': 'name,url'
            }
            
            response = requests.get(url, params=query)
            
            if response.status_code != 200:
                typer.echo(f"Erro ao obter quadros do Trello: {response.status_code}")
                raise typer.Exit(code=1)
                
            quadros = response.json()
            
            if not quadros:
                typer.echo("Nenhum quadro encontrado.")
                return
        else:
            # Usa apenas o quadro especificado
            url = f"https://api.trello.com/1/boards/{quadro_id}"
            query = {
                'key': api_key,
                'token': token,
                'fields': 'name,url'
            }
            
            response = requests.get(url, params=query)
            
            if response.status_code != 200:
                typer.echo(f"Erro ao obter o quadro especificado: {response.status_code}")
                raise typer.Exit(code=1)
                
            quadro = response.json()
            quadros = [quadro]
        
        cards_encontrados = []
        
        # Para cada quadro, busca os cards que correspondem ao termo
        for quadro in quadros:
            quadro_id = quadro['id']
            quadro_nome = quadro['name']
            
            # Obter todas as listas do quadro para mapear IDs para nomes
            listas_url = f"https://api.trello.com/1/boards/{quadro_id}/lists"
            listas_query = {
                'key': api_key,
                'token': token,
                'fields': 'name'
            }
            
            listas_response = requests.get(listas_url, params=listas_query)
            
            if listas_response.status_code != 200:
                typer.echo(f"Erro ao obter listas do quadro {quadro_nome}: {listas_response.status_code}")
                continue
                
            listas = listas_response.json()
            listas_map = {lista['id']: lista['name'] for lista in listas}
            
            # Obter todos os cards do quadro
            cards_url = f"https://api.trello.com/1/boards/{quadro_id}/cards"
            cards_query = {
                'key': api_key,
                'token': token,
                'fields': 'name,url,idList'
            }
            
            cards_response = requests.get(cards_url, params=cards_query)
            
            if cards_response.status_code != 200:
                typer.echo(f"Erro ao obter cards do quadro {quadro_nome}: {cards_response.status_code}")
                continue
                
            cards = cards_response.json()
            
            # Filtrar os cards pelo termo de busca
            for card in cards:
                if termo.lower() in card['name'].lower():
                    card_info = {
                        'nome': card['name'],
                        'quadro_nome': quadro_nome,
                        'lista_nome': listas_map.get(card['idList'], "Lista desconhecida"),
                        'url': card['url']
                    }
                    cards_encontrados.append(card_info)
        
        # Exibir resultados
        if not cards_encontrados:
            typer.echo(f"Nenhum card encontrado com o termo '{termo}'.")
            return
            
        typer.echo(f"Cards encontrados com o termo '{termo}':")
        for idx, card in enumerate(cards_encontrados, 1):
            typer.echo(f"{idx}. {card['nome']}")
            typer.echo(f"   Quadro: {card['quadro_nome']}")
            typer.echo(f"   Lista: {card['lista_nome']}")
            typer.echo(f"   URL: {card['url']}")
            if idx < len(cards_encontrados):
                typer.echo("")  # Linha em branco entre cards
    
    except Exception as e:
        typer.echo(f"Erro ao buscar cards do Trello: {str(e)}")
        raise typer.Exit(code=1)

# Função principal
def main():
    # Esta função é chamada ao executar o script diretamente
    try:
        # Carrega a configuração MCP.run
        config_file = os.path.expanduser("~/.arcee/config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    global _mcp_session_id
                    _mcp_session_id = config.get("mcp_session_id")
                    if _mcp_session_id:
                        logger.info(f"ID de sessão MCP.run carregado: {_mcp_session_id}")
            except Exception as e:
                logger.error(f"Erro ao carregar configuração MCP.run: {e}")
        
        app()
    except KeyboardInterrupt:
        logger.info("Programa encerrado pelo usuário via KeyboardInterrupt")
        print("\n👋 Programa encerrado pelo usuário")
        sys.exit(0)

if __name__ == "__main__":
    main()
