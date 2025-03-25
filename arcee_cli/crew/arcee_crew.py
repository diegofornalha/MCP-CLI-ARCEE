#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implementação da tripulação Arcee para integração com CrewAI
"""

import os
import logging
from typing import List, Dict, Any, Optional
import yaml

# Configuração de logging
logger = logging.getLogger("arcee_crew")

# Verificação condicional para importação de CrewAI
try:
    from crewai import Agent, Crew, Process, Task
    from arcee_cli.tools.mcpx_tools import get_mcprun_tools
    CREWAI_AVAILABLE = True
except ImportError:
    logger.warning("CrewAI não está disponível. Para usar este módulo, instale: pip install crewai")
    CREWAI_AVAILABLE = False
    # Classes fictícias para permitir carregamento sem CrewAI
    class Agent:
        def __init__(self, *args, **kwargs):
            pass
    class Crew:
        def __init__(self, *args, **kwargs):
            pass
    class Process:
        sequential = "sequential"
    class Task:
        def __init__(self, *args, **kwargs):
            pass


class ArceeCrew:
    """Implementação da tripulação Arcee para integração com CrewAI"""
    
    def __init__(self, 
                 config_dir: str = None, 
                 agents_file: str = "agents.yaml", 
                 tasks_file: str = "tasks.yaml",
                 session_id: Optional[str] = None,
                 process: str = "sequential"):
        """
        Inicializa a tripulação Arcee
        
        Args:
            config_dir: Diretório de configuração (padrão: ~/.arcee/config)
            agents_file: Nome do arquivo de configuração de agentes
            tasks_file: Nome do arquivo de configuração de tarefas
            session_id: ID da sessão MCP.run
            process: Tipo de processo (sequential ou hierarchical)
        """
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI não está disponível. A tripulação não funcionará.")
            return
            
        # Configuração de diretórios
        self.config_dir = config_dir or os.path.expanduser("~/.arcee/config")
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
            
        # Arquivos de configuração
        self.agents_file = os.path.join(self.config_dir, agents_file)
        self.tasks_file = os.path.join(self.config_dir, tasks_file)
        
        # Cria arquivos de configuração padrão se não existirem
        self._ensure_config_files()
        
        # Carrega ferramentas MCP.run
        self.session_id = session_id
        self.mcpx_tools = get_mcprun_tools(session_id=session_id)
        
        # Define o processo
        if process == "hierarchical":
            self.process = Process.hierarchical
        else:
            self.process = Process.sequential
            
        # Carrega configurações
        self.agents_config = self._load_yaml(self.agents_file)
        self.tasks_config = self._load_yaml(self.tasks_file)
        
        # Inicializa agentes e tarefas
        self.agents = []
        self.tasks = []
        
        # Cria a tripulação
        self.crew = None

    def _ensure_config_files(self):
        """Garante que os arquivos de configuração existam"""
        if not os.path.exists(self.agents_file):
            logger.info(f"Criando arquivo de configuração de agentes: {self.agents_file}")
            default_agents = {
                "assistente": {
                    "role": "Assistente Virtual",
                    "goal": "Ajudar o usuário com suas tarefas",
                    "backstory": "Você é um assistente virtual inteligente que ajuda o usuário em diversas tarefas."
                }
            }
            self._save_yaml(self.agents_file, default_agents)
            
        if not os.path.exists(self.tasks_file):
            logger.info(f"Criando arquivo de configuração de tarefas: {self.tasks_file}")
            default_tasks = {
                "pesquisa": {
                    "description": "Realizar pesquisa sobre um tópico fornecido pelo usuário",
                    "expected_output": "Informações detalhadas sobre o tópico pesquisado",
                    "agent": "assistente"
                }
            }
            self._save_yaml(self.tasks_file, default_tasks)

    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Carrega um arquivo YAML"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Arquivo não encontrado: {file_path}")
                return {}
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo YAML {file_path}: {e}")
            return {}
            
    def _save_yaml(self, file_path: str, data: Dict[str, Any]):
        """Salva um dicionário em um arquivo YAML"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo YAML {file_path}: {e}")

    def create_agents(self):
        """Cria os agentes a partir da configuração"""
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI não está disponível. Não é possível criar agentes.")
            return
            
        self.agents = []
        for name, config in self.agents_config.items():
            # Determina se este agente deve ter acesso às ferramentas MCP.run
            has_tools = config.get("has_tools", True)
            tools = self.mcpx_tools if has_tools else None
            
            agent = Agent(
                name=name,
                role=config.get("role", "Assistente"),
                goal=config.get("goal", "Ajudar o usuário"),
                backstory=config.get("backstory", ""),
                verbose=config.get("verbose", True),
                tools=tools
            )
            self.agents.append(agent)
            logger.info(f"Agente criado: {name}")
            
        return self.agents

    def create_tasks(self):
        """Cria as tarefas a partir da configuração"""
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI não está disponível. Não é possível criar tarefas.")
            return
            
        self.tasks = []
        
        # Encontra os agentes pelo nome
        agent_map = {agent.name: agent for agent in self.agents}
        
        for name, config in self.tasks_config.items():
            # Obtém o agente responsável
            agent_name = config.get("agent")
            agent = agent_map.get(agent_name)
            
            if not agent:
                logger.warning(f"Agente '{agent_name}' não encontrado para a tarefa '{name}'")
                continue
                
            task = Task(
                description=config.get("description", ""),
                expected_output=config.get("expected_output", ""),
                agent=agent
            )
            self.tasks.append(task)
            logger.info(f"Tarefa criada: {name} (agente: {agent_name})")
            
        return self.tasks

    def create_crew(self):
        """Cria a tripulação com os agentes e tarefas"""
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI não está disponível. Não é possível criar a tripulação.")
            return
            
        if not self.agents:
            self.create_agents()
            
        if not self.tasks:
            self.create_tasks()
            
        self.crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=self.process,
            verbose=True
        )
        logger.info(f"Tripulação criada com {len(self.agents)} agentes e {len(self.tasks)} tarefas")
        return self.crew

    def run(self, inputs: Optional[Dict[str, Any]] = None) -> str:
        """Executa a tripulação"""
        if not CREWAI_AVAILABLE:
            return "Erro: CrewAI não está disponível. Instale: pip install crewai"
            
        if not self.crew:
            self.create_crew()
            
        logger.info("Iniciando execução da tripulação...")
        try:
            result = self.crew.run(inputs=inputs)
            logger.info("Execução da tripulação concluída com sucesso")
            return result
        except Exception as e:
            logger.error(f"Erro na execução da tripulação: {e}")
            return f"Erro na execução da tripulação: {e}" 