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
    logger.warning("Módulo crewAI não está disponível, funcionalidades de crew desativadas")

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
                logger.info("Usuário encerrou o chat")
                break

            logger.debug(f"Mensagem do usuário: {user_input}")
            messages.append({"role": "user", "content": user_input})
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


if __name__ == "__main__":
    try:
        # Carrega a configuração MCP.run
        config_file = os.path.expanduser("~/.arcee/config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
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
