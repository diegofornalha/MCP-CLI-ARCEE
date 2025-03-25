#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerenciador de equipes de agentes para o Arcee CLI usando crewAI
"""

from typing import List, Dict, Any, Optional, Tuple
import json
from crewai import Crew, Agent, Task, Process
from crewai.tools import BaseTool

from arcee_cli.infrastructure.providers.arcee_provider import ArceeProvider
from mcp_server_cursor.veyrax_mcp_server.tools import VeyraXTools
from .arcee_agents import (
    create_tooling_agent,
    create_research_agent,
    create_coding_agent,
)


class ArceeCrew:
    """
    Gerenciador de equipes de agentes para o Arcee CLI
    """

    def __init__(self, provider: Optional[ArceeProvider] = None):
        """
        Inicializa o gerenciador de equipes com um provedor Arcee opcional

        Args:
            provider: Um provedor do Arcee para comunicação com a API
        """
        self.provider = provider or ArceeProvider()
        self.tools = VeyraXTools().get_tools()

        # Inicializa os agentes com as ferramentas
        self.tooling_agent = create_tooling_agent(self.tools)
        self.research_agent = create_research_agent(self.tools)
        self.coding_agent = create_coding_agent(self.tools)

    def create_crew(self, process: Process = Process.sequential) -> Crew:
        """
        Cria uma equipe com todos os agentes disponíveis

        Args:
            process: Processo de execução da equipe (sequential, hierarchical)

        Returns:
            Crew: Uma equipe do crewAI com todos os agentes
        """
        # Cria a equipe com todos os agentes
        crew = Crew(
            agents=[self.tooling_agent, self.research_agent, self.coding_agent],
            tasks=[],  # Tarefas serão adicionadas depois
            verbose=True,
            process=process,
            memory=True,  # Habilita memória para que os agentes se lembrem do histórico
        )

        return crew

    def add_task(self, crew: Crew, description: str, agent_name: str = None) -> Task:
        """
        Adiciona uma tarefa à equipe

        Args:
            crew: Equipe a receber a tarefa
            description: Descrição da tarefa
            agent_name: Nome do agente designado para a tarefa (opcional)

        Returns:
            Task: A tarefa criada
        """
        # Determina qual agente usar para a tarefa
        agent = None
        if agent_name:
            if agent_name.lower() == "ferramentas" or agent_name.lower() == "tooling":
                agent = self.tooling_agent
            elif agent_name.lower() == "pesquisa" or agent_name.lower() == "research":
                agent = self.research_agent
            elif agent_name.lower() == "codigo" or agent_name.lower() == "coding":
                agent = self.coding_agent

        # Cria a tarefa
        task = Task(
            description=description,
            agent=agent,  # Se agent for None, a equipe decidirá qual agente usar
            expected_output="Resultado detalhado da tarefa, incluindo todas as etapas realizadas.",
        )

        # Adiciona à lista de tarefas da equipe
        crew.tasks.append(task)

        return task

    def execute(self, crew: Crew, inputs: Optional[Dict[str, Any]] = None) -> str:
        """
        Executa as tarefas da equipe

        Args:
            crew: Equipe a ser executada
            inputs: Entradas para a execução

        Returns:
            str: Resultado da execução
        """
        # Executa a equipe
        result = crew.kickoff(inputs=inputs or {})
        return result

    def process_user_command(self, user_input: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Processa um comando do usuário para criar uma equipe e executar tarefas

        Args:
            user_input: Entrada do usuário

        Returns:
            Tuple[bool, Dict[str, Any]]: Tupla com (sucesso, resultado)
        """
        try:
            # Tenta processar como um comando JSON para criar uma equipe customizada
            if user_input.startswith("{") and user_input.endswith("}"):
                try:
                    # Tenta parsear JSON
                    crew_config = json.loads(user_input)

                    # Verifica se tem as chaves necessárias
                    if "tasks" not in crew_config:
                        return False, {
                            "error": "Configuração de equipe inválida. Falta a chave 'tasks'."
                        }

                    # Cria a equipe
                    process_type = Process.sequential
                    if crew_config.get("process") == "hierarchical":
                        process_type = Process.hierarchical

                    crew = self.create_crew(process=process_type)

                    # Adiciona as tarefas
                    for task_config in crew_config["tasks"]:
                        description = task_config.get("description")
                        if not description:
                            return False, {"error": "Tarefa sem descrição"}

                        agent_name = task_config.get("agent")
                        self.add_task(crew, description, agent_name)

                    # Executa a equipe
                    inputs = crew_config.get("inputs", {})
                    result = self.execute(crew, inputs)

                    return True, {"result": result}

                except json.JSONDecodeError:
                    pass  # Não é um JSON válido, continua para o próximo formato

            # Formato simples: criar uma única tarefa
            # Cria uma equipe com uma única tarefa
            crew = self.create_crew()
            self.add_task(crew, user_input)
            result = self.execute(crew)

            return True, {"result": result}

        except Exception as e:
            return False, {"error": f"Erro ao processar comando: {str(e)}"}
