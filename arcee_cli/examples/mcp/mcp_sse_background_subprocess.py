#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemplo de como executar o cliente SSE do MCP.run em segundo plano usando subprocess.

Este script demonstra como iniciar o cliente SSE como um processo separado
que continua em execução mesmo após o script principal terminar.
"""

import os
import sys
import subprocess
import signal
import time
import dotenv
import atexit

# Carrega variáveis de ambiente do arquivo .env
dotenv.load_dotenv()

# Verifica se o arquivo de cliente SSE existe
CLIENTE_SSE_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_sse_app.py")
if not os.path.exists(CLIENTE_SSE_SCRIPT):
    print(f"❌ Erro: Script do cliente SSE não encontrado: {CLIENTE_SSE_SCRIPT}")
    sys.exit(1)

# Armazena referência ao processo em segundo plano
processo_sse = None


def encerrar_processo():
    """Encerra o processo em segundo plano se estiver em execução"""
    global processo_sse
    if processo_sse:
        print("\nEncerrando processo do cliente SSE...")
        try:
            # Envia sinal SIGTERM para encerrar graciosamente
            processo_sse.terminate()
            # Aguarda até 3 segundos pelo encerramento
            processo_sse.wait(timeout=3)
        except subprocess.TimeoutExpired:
            # Se não encerrou, força o encerramento
            print("Forçando encerramento do processo...")
            processo_sse.kill()
        except Exception as e:
            print(f"Erro ao encerrar processo: {e}")


def iniciar_cliente_sse_background():
    """Inicia o cliente SSE em segundo plano como um processo separado"""
    global processo_sse
    
    # Configura o comando a ser executado
    comando = [sys.executable, CLIENTE_SSE_SCRIPT]
    
    print(f"Iniciando cliente SSE em segundo plano: {' '.join(comando)}")
    
    try:
        # Inicia o processo redirecionando saída para arquivo de log
        with open("sse_client.log", "w") as log_file:
            processo_sse = subprocess.Popen(
                comando,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                # Desvincula o processo do terminal atual
                start_new_session=True
            )
        
        # Verifica se o processo iniciou corretamente
        if processo_sse.poll() is not None:
            print(f"❌ Erro: O processo encerrou imediatamente com código {processo_sse.returncode}")
            return False
            
        print(f"✅ Processo iniciado com PID: {processo_sse.pid}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao iniciar processo em segundo plano: {e}")
        return False


def main():
    """Função principal"""
    print("=== Cliente SSE MCP.run em Segundo Plano (Subprocess) ===")
    
    # Registra função para encerrar o processo ao sair
    atexit.register(encerrar_processo)
    
    # Configura handler para CTRL+C
    def handler_sigint(signum, frame):
        print("\n⚠️ Interrompido pelo usuário.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handler_sigint)
    
    # Inicia o cliente SSE em segundo plano
    if not iniciar_cliente_sse_background():
        sys.exit(1)
    
    print("\n✅ Cliente SSE iniciado em segundo plano!")
    print("📝 Os logs estão sendo escritos em: sse_client.log")
    print("🔄 A aplicação principal pode executar outras tarefas...")
    print("(Pressione Ctrl+C para encerrar)")
    
    try:
        # Simula a aplicação principal fazendo outras tarefas
        contador = 0
        while True:
            contador += 1
            print(f"Aplicação principal realizando outras tarefas... (ciclo {contador})")
            time.sleep(3)  # Simula trabalho sendo feito
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário")
    
    print("✅ Aplicação encerrada com sucesso")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 