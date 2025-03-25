#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicação cliente SSE para MCP.run com execução em segundo plano.

Esta aplicação demonstra como executar o cliente SSE do MCP.run em segundo plano,
permitindo que a aplicação principal continue executando outras tarefas enquanto
os eventos são processados assincronamente.
"""

import sys
import os
import json
import time
import signal
import threading
import dotenv
from typing import Dict, Any, cast, Optional

# Carrega variáveis de ambiente do arquivo .env
dotenv.load_dotenv()

# Importação do cliente SSE do pacote arcee_cli
from arcee_cli.infrastructure.mcp import MCPRunSSEClient, Evento

# Obtém a URL SSE do MCP.run das variáveis de ambiente
SSE_URL = os.getenv("MCP_SSE_URL")
if not SSE_URL:
    print("❌ Erro: Variável de ambiente MCP_SSE_URL não configurada no arquivo .env")
    sys.exit(1)

# SSE_URL já foi verificado não-nulo acima, então é seguro fazer o cast
SSE_URL = cast(str, SSE_URL)

# Variáveis para controle do serviço em segundo plano
cliente_sse: Optional[MCPRunSSEClient] = None
thread_processamento: Optional[threading.Thread] = None
encerrar_servico = threading.Event()


def processar_evento(evento: Evento) -> None:
    """
    Processa um evento recebido do MCP.run
    
    Args:
        evento: Evento recebido via SSE
    """
    print(f"\n--- Novo Evento [{evento.event_type}] ---")
    
    # Tenta processar como JSON
    json_data = evento.json
    if json_data:
        # Formato simplificado para log
        if isinstance(json_data, dict):
            tipo = json_data.get('type', 'desconhecido')
            mensagem = json_data.get('message', 'sem mensagem')
            print(f"Evento tipo '{tipo}': {mensagem}")
    else:
        # Imprime os dados brutos se não for JSON
        print(f"Dados (Raw): {evento.data[:100]}...")


def thread_processamento_eventos() -> None:
    """Thread que processa eventos em segundo plano"""
    global cliente_sse
    
    if not cliente_sse:
        print("❌ Cliente SSE não inicializado")
        return
    
    print("✅ Iniciando processamento de eventos em segundo plano...")
    
    try:
        # Processa eventos enquanto o sinalizador de encerramento não estiver ativo
        while not encerrar_servico.is_set() and cliente_sse.running:
            cliente_sse.processar_eventos(processar_evento, timeout=0.5)
            # Pequena pausa para não consumir CPU desnecessariamente
            time.sleep(0.1)
    except Exception as e:
        print(f"❌ Erro no processamento em segundo plano: {e}")
    
    print("Thread de processamento de eventos encerrada")


def iniciar_servico_background() -> bool:
    """
    Inicia o serviço SSE em segundo plano
    
    Returns:
        True se iniciado com sucesso, False caso contrário
    """
    global cliente_sse, thread_processamento
    
    # Encerra serviço existente se estiver rodando
    if thread_processamento and thread_processamento.is_alive():
        encerrar_servico_background()
    
    # Reseta o sinalizador de encerramento
    encerrar_servico.clear()
    
    # Cria e inicia o cliente SSE
    cliente_sse = MCPRunSSEClient(SSE_URL)
    if not cliente_sse.iniciar():
        print("❌ Falha ao iniciar o cliente SSE")
        return False
    
    # Inicia a thread de processamento
    thread_processamento = threading.Thread(
        target=thread_processamento_eventos,
        daemon=True  # Thread daemon encerra quando o programa principal encerra
    )
    thread_processamento.start()
    
    return True


def encerrar_servico_background() -> None:
    """Encerra o serviço SSE em segundo plano"""
    global cliente_sse, thread_processamento
    
    # Sinaliza para a thread encerrar
    encerrar_servico.set()
    
    # Encerra o cliente SSE
    if cliente_sse:
        cliente_sse.parar()
    
    # Espera a thread terminar (com timeout)
    if thread_processamento and thread_processamento.is_alive():
        thread_processamento.join(timeout=2.0)


def configurar_sinais() -> None:
    """Configura handlers para sinais do sistema operacional"""
    def handler_sigint(signum, frame):
        print("\n⚠️ Sinal de interrupção recebido. Encerrando...")
        encerrar_servico_background()
        sys.exit(0)
    
    # Registra o handler para SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, handler_sigint)


def main() -> int:
    """Função principal da aplicação"""
    print("=== Cliente SSE MCP.run em Segundo Plano ===")
    
    # Configura handlers para sinais
    configurar_sinais()
    
    # Inicia o serviço em segundo plano
    if not iniciar_servico_background():
        return 1
    
    print("\n✅ Serviço SSE iniciado em segundo plano!")
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
    finally:
        # Encerra o serviço em segundo plano
        encerrar_servico_background()
    
    print("✅ Aplicação encerrada com sucesso")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 