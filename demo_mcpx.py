#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de demonstração para testar a integração MCP.run

Este script pode ser executado diretamente para testar a integração MCP.run
sem depender de outras partes do projeto.
"""

import logging
import sys
import json
import os
import subprocess
from typing import Dict, List, Any, Optional

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("demo_mcpx")

class MCPxDemo:
    """Cliente simplificado para demonstração do MCP.run"""
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Inicializa o cliente MCP.run
        
        Args:
            session_id: ID de sessão opcional
        """
        self.session_id = session_id
        
    def generate_session(self) -> Optional[str]:
        """
        Gera um ID de sessão MCP.run
        
        Returns:
            ID de sessão gerado ou None em caso de erro
        """
        try:
            logger.info("Gerando nova sessão MCP.run...")
            cmd = "npx --yes -p @dylibso/mcpx@latest gen-session"
            print(f"Executando: {cmd}")
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                check=True, 
                text=True, 
                capture_output=True
            )
            
            # Extrai o ID de sessão da saída
            output = result.stdout
            if "mcpx/" in output:
                session_id = output.strip().split("\n")[-1].strip()
                logger.info(f"Nova sessão MCP.run gerada: {session_id}")
                self.session_id = session_id
                return session_id
            else:
                logger.error(f"Não foi possível extrair o ID de sessão da saída.")
                print("Saída do comando:")
                print(output)
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao gerar sessão MCP.run: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return None
        except Exception as e:
            logger.exception(f"Erro ao gerar sessão MCP.run: {e}")
            return None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lista as ferramentas disponíveis
        
        Returns:
            Lista de ferramentas disponíveis
        """
        try:
            # Verifica se temos uma sessão
            if not self.session_id:
                logger.error("Nenhum ID de sessão configurado")
                return []

            # Executa o comando para listar ferramentas
            cmd = f"npx mcpx tools --session {self.session_id}"
            logger.info(f"Executando: {cmd}")
            
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                text=True,
                capture_output=True
            )
            
            # Processa a saída
            output = result.stdout
            tools = []
            
            # Tenta extrair o JSON da saída
            json_start = output.find('{')
            if json_start >= 0:
                json_str = output[json_start:]
                try:
                    data = json.loads(json_str)
                    
                    if "tools" in data:
                        for name, info in data["tools"].items():
                            tools.append({
                                "name": name,
                                "description": info.get("description", ""),
                                "schema": info.get("schema", {})
                            })
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {e}")
            
            return tools
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao listar ferramentas: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return []
        except Exception as e:
            logger.exception(f"Erro ao listar ferramentas: {e}")
            return []
    
    def run_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ferramenta
        
        Args:
            tool_name: Nome da ferramenta
            params: Parâmetros da ferramenta
            
        Returns:
            Resultado da execução
        """
        try:
            # Verifica se temos uma sessão
            if not self.session_id:
                logger.error("Nenhum ID de sessão configurado")
                return {"error": "Nenhum ID de sessão configurado"}
                
            # Salva os parâmetros em um arquivo temporário
            params_file = "temp_params.json"
            with open(params_file, "w", encoding="utf-8") as f:
                json.dump(params, f)
                
            # Executa o comando
            cmd = f"npx mcpx run {tool_name} --file {params_file} --session {self.session_id}"
            logger.info(f"Executando ferramenta: {tool_name}")
            logger.debug(f"Parâmetros: {params}")
            logger.debug(f"Comando: {cmd}")
            
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                text=True,
                capture_output=True
            )
            
            # Processa a saída
            output = result.stdout
            
            # Tenta extrair o JSON da saída
            json_start = output.find('{')
            if json_start >= 0:
                json_str = output[json_start:]
                try:
                    data = json.loads(json_str)
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {e}")
            
            return {"error": "Formato de resposta não reconhecido", "raw_output": output}
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar ferramenta: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return {"error": str(e)}
        except Exception as e:
            logger.exception(f"Erro ao executar ferramenta: {e}")
            return {"error": str(e)}
        finally:
            # Remove o arquivo temporário se existir
            if os.path.exists(params_file):
                os.remove(params_file)

def main():
    """Função principal de demonstração"""
    print("=== Demonstração da Integração MCP.run ===\n")
    
    # Tenta carregar ID de sessão existente
    session_id = None
    config_file = os.path.expanduser("~/.arcee/config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                session_id = config.get("mcp_session_id")
                if session_id:
                    print(f"ID de sessão existente encontrado: {session_id}")
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
    
    # Cria o cliente de demonstração
    demo = MCPxDemo(session_id)
    
    # Se não temos um ID de sessão, gera um novo
    if not demo.session_id:
        print("\n1. Gerando nova sessão MCP.run...")
        session_id = demo.generate_session()
        if not session_id:
            print("❌ Falha ao gerar sessão MCP.run. Encerrando.")
            return
        
        # Salva o ID de sessão
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump({"mcp_session_id": session_id}, f, indent=2)
            print(f"✅ ID de sessão salvo em {config_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    # Lista as ferramentas disponíveis
    print("\n2. Listando ferramentas disponíveis...")
    tools = demo.list_tools()
    if not tools:
        print("❌ Nenhuma ferramenta disponível ou erro ao listar ferramentas.")
        return
        
    print(f"✅ {len(tools)} ferramentas disponíveis:")
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool['name']} - {tool['description']}")
    
    # Pergunta se o usuário quer executar alguma ferramenta
    if tools:
        print("\n3. Deseja executar alguma ferramenta? (s/n)")
        choice = input("> ").strip().lower()
        
        if choice == "s":
            print("\nEscolha o número da ferramenta:")
            try:
                index = int(input("> ").strip()) - 1
                if 0 <= index < len(tools):
                    tool = tools[index]
                    print(f"\nExecutando {tool['name']}...")
                    
                    # Exemplo simples com parâmetros
                    params = {}
                    print(f"Ferramenta selecionada: {tool['name']}")
                    print("Esta é uma demonstração simples. Em um caso real, você forneceria parâmetros específicos.")
                    
                    # Executa a ferramenta
                    result = demo.run_tool(tool['name'], params)
                    
                    if "error" in result:
                        print(f"❌ Erro ao executar ferramenta: {result['error']}")
                    else:
                        print("✅ Resultado:")
                        print(json.dumps(result, indent=2))
                else:
                    print("❌ Índice inválido.")
            except (ValueError, IndexError) as e:
                print(f"❌ Erro ao selecionar ferramenta: {e}")
    
    print("\n=== Demonstração concluída ===")

if __name__ == "__main__":
    main() 