#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integração simplificada com MCP.run
"""

import subprocess
import json
import logging
import os
import threading
import queue
import time
from typing import Dict, Any, List, Optional, Callable

# Configuração de logging
logger = logging.getLogger("mcpx_simple")

def run_command_with_timeout(cmd: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Executa um comando com timeout usando threads
    
    Args:
        cmd: Comando a ser executado
        timeout: Tempo máximo de execução em segundos
        
    Returns:
        Resultado da execução
    """
    result_queue = queue.Queue()
    
    def target():
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            result_queue.put({
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr
            })
        except Exception as e:
            result_queue.put({"error": str(e)})
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    
    try:
        result = result_queue.get(timeout=timeout)
        if "error" in result:
            return {"error": result["error"]}
        
        if result["returncode"] != 0:
            return {"error": f"Comando falhou com código {result['returncode']}", "stderr": result["stderr"]}
        
        return {"stdout": result["stdout"], "stderr": result["stderr"]}
    except queue.Empty:
        return {"error": f"Timeout: o comando excedeu {timeout} segundos", "command": cmd}

class MCPRunClient:
    """Cliente simplificado para MCP.run"""
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Inicializa o cliente MCP.run
        
        Args:
            session_id: ID de sessão opcional
        """
        self.session_id = session_id
        self._tools_cache = None
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de ferramentas disponíveis
        
        Returns:
            Lista de ferramentas disponíveis
        """
        if self._tools_cache is not None:
            return self._tools_cache
            
        try:
            # Usa npx para listar as ferramentas
            cmd = f"npx mcpx tools"
            if self.session_id:
                cmd += f" --session {self.session_id}"
                
            logger.debug(f"Executando comando: {cmd}")
            
            result = run_command_with_timeout(cmd)
            
            if "error" in result:
                logger.error(f"Erro ao executar comando: {result['error']}")
                return []
            
            # Tenta extrair a saída JSON
            tools = []
            try:
                # A saída pode conter texto antes do JSON
                output = result["stdout"]
                logger.debug(f"Output bruto do comando: {output[:200]}...")
                
                # Encontra o início do JSON (primeiro '{')
                json_start = output.find('{')
                if json_start >= 0:
                    json_str = output[json_start:]
                    data = json.loads(json_str)
                    
                    # Extrai as ferramentas
                    if isinstance(data, dict) and "tools" in data:
                        tools = []
                        
                        # Log detalhado das ferramentas disponíveis
                        logger.debug(f"Ferramentas disponíveis: {list(data['tools'].keys())}")
                        
                        for name, info in data["tools"].items():
                            tools.append({
                                "name": name,
                                "description": info.get("description", ""),
                                "schema": info.get("schema", {})
                            })
                
                logger.info(f"Encontradas {len(tools)} ferramentas")
                self._tools_cache = tools
                return tools
            except json.JSONDecodeError:
                logger.error(f"Erro ao decodificar saída JSON: {output}")
                return []
                
        except Exception as e:
            logger.exception(f"Erro ao obter ferramentas: {e}")
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
            # Salva os parâmetros em um arquivo temporário
            params_file = os.path.expanduser("~/.arcee/temp_params.json")
            os.makedirs(os.path.dirname(params_file), exist_ok=True)
            
            with open(params_file, "w", encoding="utf-8") as f:
                json.dump(params, f)
            
            # Monta o comando
            cmd = f"npx mcpx run {tool_name} --file {params_file}"
            if self.session_id:
                cmd += f" --session {self.session_id}"
                
            logger.debug(f"Executando ferramenta: {tool_name} com parâmetros: {params}")
            logger.debug(f"Comando: {cmd}")
            
            # Executa o comando com nossa função personalizada de timeout
            result = run_command_with_timeout(cmd, timeout=60)
            
            if "error" in result:
                logger.error(f"Erro na execução do comando: {result['error']}")
                return {"error": result["error"]}
            
            # Tenta extrair a saída JSON
            try:
                output = result["stdout"]
                # Encontra o início do JSON (primeiro '{')
                json_start = output.find('{')
                if json_start >= 0:
                    json_str = output[json_start:]
                    data = json.loads(json_str)
                    return data
                    
                logger.warning(f"Não foi possível encontrar JSON na saída: {output}")
                return {"error": "Saída não é um JSON válido", "raw_output": output}
            except json.JSONDecodeError:
                logger.error(f"Erro ao decodificar saída JSON: {result['stdout']}")
                return {"error": "Erro ao decodificar JSON", "raw_output": result["stdout"]}
                
        except Exception as e:
            logger.exception(f"Erro ao executar ferramenta: {e}")
            return {"error": str(e)}
        finally:
            # Remove o arquivo temporário se existir
            if os.path.exists(params_file):
                try:
                    os.remove(params_file)
                except:
                    pass

def configure_mcprun(session_id: Optional[str] = None) -> Optional[str]:
    """
    Configura o MCP.run obtendo ou utilizando um ID de sessão
    
    Args:
        session_id: ID de sessão opcional existente
        
    Returns:
        ID de sessão configurado ou None em caso de erro
    """
    if session_id:
        logger.info(f"Usando ID de sessão fornecido: {session_id}")
        return session_id
        
    try:
        # Gera um novo ID de sessão
        logger.info("Gerando nova sessão MCP.run...")
        cmd = "npx --yes -p @dylibso/mcpx@latest gen-session"
        
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
            # O token normalmente aparece como "mcpx/username/token"
            session_id = output.strip().split("\n")[-1].strip()
            logger.info(f"Sessão MCP.run gerada: {session_id}")
            return session_id
        else:
            logger.error(f"Não foi possível extrair o ID de sessão da saída: {output}")
            return None
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao gerar sessão MCP.run: {e}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        return None
    except Exception as e:
        logger.exception(f"Erro ao configurar MCP.run: {e}")
        return None 