#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente para conexão com endpoints SSE (Server-Sent Events) do MCP.run.

Este módulo fornece uma implementação para conectar, gerenciar e 
processar eventos SSE do MCP.run, facilitando a integração com aplicações.
"""

import logging
import sys
import json
import time
import queue
from typing import Dict, List, Any, Optional, Callable, Generator
import threading
from urllib.parse import urlparse

import requests

# Configuração básica de logging caso não esteja configurado
try:
    # Tenta importar o módulo de logging do projeto
    sys.path.append(".")
    from arcee_cli.infrastructure.logging_config import obter_logger
    logger = obter_logger("mcp_sse")
except ImportError:
    # Configura um logger básico se o módulo não estiver disponível
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )
    logger = logging.getLogger("mcp_sse")


class Evento:
    """Representa um evento recebido do MCP.run via SSE"""
    
    def __init__(self, event_type: str, data: Any, id: Optional[str] = None):
        """
        Inicializa um novo evento
        
        Args:
            event_type: Tipo do evento (normalmente 'message' para SSE)
            data: Dados do evento (normalmente uma string JSON)
            id: Identificador do evento (opcional)
        """
        self.event_type = event_type
        self.data = data
        self.id = id
    
    def __str__(self) -> str:
        """Representação em string do evento"""
        return f"Evento[{self.event_type}]: {self.data[:50]}..."
    
    @property
    def json(self) -> Any:
        """Tenta converter os dados para JSON"""
        if isinstance(self.data, str):
            try:
                return json.loads(self.data)
            except json.JSONDecodeError:
                return None
        return self.data


class MCPRunSSEClient:
    """Cliente para conexão com endpoints SSE do MCP.run"""
    
    def __init__(self, sse_url: str, timeout: int = 30):
        """
        Inicializa o cliente SSE para MCP.run
        
        Args:
            sse_url: URL completa do endpoint SSE, incluindo parâmetros de autenticação
            timeout: Tempo limite para conexão em segundos
        """
        self.sse_url = sse_url
        self.timeout = timeout
        self.running = False
        self.last_id = None
        self.retry_delay = 3  # Segundos entre tentativas de reconexão
        self.max_retries = 5  # Número máximo de tentativas de reconexão
        self.eventos_queue = queue.Queue()  # Fila para eventos recebidos
        self._thread = None
        self._validate_url()
        
    def _validate_url(self) -> None:
        """Valida a URL do SSE"""
        parsed = urlparse(self.sse_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("URL SSE inválida")
        
        if not parsed.query or "nonce" not in parsed.query:
            logger.warning("URL SSE pode não conter parâmetros de autenticação necessários")
        
        # Verificações específicas para MCP.run
        if "mcp.run" not in parsed.netloc:
            logger.warning("A URL não parece ser do domínio mcp.run")
    
    def _parse_sse_line(self, line: str) -> Dict[str, str]:
        """
        Processa uma linha do SSE
        
        Args:
            line: Linha recebida do stream SSE
            
        Returns:
            Dicionário com campos da linha processada
        """
        if not line:
            return {}
            
        # Parse SSE line (field: value)
        if ":" not in line:
            return {"field": line, "value": ""}
            
        field, value = line.split(":", 1)
        if value.startswith(" "):
            value = value[1:]  # Remove o espaço depois do ':'
            
        return {"field": field, "value": value}
    
    def _process_sse_stream(self, response: requests.Response) -> Generator[Evento, None, None]:
        """
        Processa o stream SSE
        
        Args:
            response: Resposta HTTP com o stream SSE
            
        Yields:
            Eventos extraídos do stream
        """
        event_data = ""
        event_type = "message"  # Tipo padrão
        event_id = None
        
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                # Linhas vazias indicam final de um evento
                if event_data:
                    # Entrega o evento
                    event = Evento(event_type, event_data, event_id)
                    self.last_id = event_id
                    yield event
                    
                    # Limpa os dados para o próximo evento
                    event_data = ""
                    event_type = "message"
                    event_id = None
                continue
                
            parsed_line = self._parse_sse_line(line)
            field, value = parsed_line.get("field", ""), parsed_line.get("value", "")
            
            if field == "event":
                event_type = value
            elif field == "data":
                event_data += value + "\n"
            elif field == "id":
                event_id = value
            elif field == "retry":
                try:
                    self.retry_delay = int(value) / 1000  # Valor em ms para segundos
                except ValueError:
                    pass
    
    def _sse_worker(self) -> None:
        """
        Thread worker para manter a conexão SSE
        
        Gerencia conexão, reconexão e processamento de eventos
        """
        retries = 0
        
        while self.running and retries < self.max_retries:
            try:
                # Prepara os headers
                headers = {
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache"
                }
                
                # Adiciona o último ID se disponível para retomar o stream
                if self.last_id:
                    headers["Last-Event-ID"] = self.last_id
                
                # Inicia a requisição com streaming
                logger.info(f"Conectando ao endpoint SSE: {self.sse_url}")
                with requests.get(
                    self.sse_url, 
                    headers=headers, 
                    stream=True, 
                    timeout=self.timeout
                ) as response:
                    # Verifica se a conexão foi bem sucedida
                    if response.status_code != 200:
                        logger.error(f"Falha na conexão SSE: HTTP {response.status_code}")
                        raise ConnectionError(f"HTTP {response.status_code}")
                    
                    # Processa eventos em streaming
                    retries = 0  # Reset das tentativas quando conectado com sucesso
                    logger.info("Conexão SSE estabelecida, aguardando eventos")
                    
                    for evento in self._process_sse_stream(response):
                        if not self.running:
                            break
                        # Coloca o evento na fila para processamento
                        self.eventos_queue.put(evento)
                        
            except (requests.RequestException, ConnectionError) as e:
                if not self.running:
                    break
                    
                retries += 1
                logger.error(f"Erro na conexão SSE (tentativa {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    logger.info(f"Tentando reconexão em {self.retry_delay} segundos...")
                    time.sleep(self.retry_delay)
                    
        # Se saímos do loop e ainda estamos em execução, registra falha permanente
        if self.running:
            logger.error("Falha permanente na conexão SSE após múltiplas tentativas")
            self.running = False
            
        logger.info("Worker SSE encerrado")
    
    def iniciar(self) -> bool:
        """
        Inicia a conexão SSE
        
        Returns:
            True se a conexão foi iniciada, False caso contrário
        """
        if self.running:
            logger.warning("Cliente SSE já está em execução")
            return True
            
        self.running = True
        # Inicia o thread para conexão SSE
        self._thread = threading.Thread(target=self._sse_worker, daemon=True)
        self._thread.start()
        return True
    
    def parar(self) -> None:
        """Encerra a conexão SSE"""
        if not self.running:
            return
            
        self.running = False
        logger.info("Solicitado encerramento da conexão SSE")
        
        # Espera pelo thread, mas com timeout para evitar bloqueio
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
    
    def processar_eventos(self, callback: Callable[[Evento], None], timeout: Optional[float] = None) -> None:
        """
        Processa eventos recebidos usando um callback
        
        Args:
            callback: Função para processar cada evento
            timeout: Tempo limite em segundos para aguardar por eventos
        """
        if not self.running:
            logger.warning("Cliente SSE não está em execução")
            return
            
        try:
            # Tenta obter um evento da fila
            evento = self.eventos_queue.get(block=True, timeout=timeout)
            # Chama o callback com o evento
            callback(evento)
            # Marca o evento como processado
            self.eventos_queue.task_done()
        except queue.Empty:
            # Timeout atingido sem eventos
            pass
        
    def processar_eventos_loop(self, callback: Callable[[Evento], None], 
                              intervalo_vazio: float = 0.1) -> None:
        """
        Processa eventos em um loop contínuo
        
        Args:
            callback: Função para processar cada evento
            intervalo_vazio: Tempo em segundos para esperar quando não há eventos
        """
        while self.running:
            try:
                # Tenta obter um evento da fila
                evento = self.eventos_queue.get(block=True, timeout=intervalo_vazio)
                # Chama o callback com o evento
                callback(evento)
                # Marca o evento como processado
                self.eventos_queue.task_done()
            except queue.Empty:
                # Nenhum evento disponível, aguarda um pouco
                pass

    def receber_eventos(self, max_eventos: int = 10, timeout: float = 5.0) -> List[Evento]:
        """
        Recebe eventos sem processá-los
        
        Args:
            max_eventos: Número máximo de eventos a receber
            timeout: Tempo limite em segundos para aguardar por eventos
            
        Returns:
            Lista de eventos recebidos
        """
        if not self.running:
            logger.warning("Cliente SSE não está em execução")
            return []
            
        eventos = []
        tempo_inicio = time.time()
        tempo_restante = timeout
        
        while len(eventos) < max_eventos and tempo_restante > 0:
            try:
                # Tenta obter um evento da fila
                evento = self.eventos_queue.get(block=True, timeout=tempo_restante)
                eventos.append(evento)
                # Marca o evento como processado
                self.eventos_queue.task_done()
                
                # Atualiza o tempo restante
                tempo_restante = timeout - (time.time() - tempo_inicio)
            except queue.Empty:
                # Timeout atingido sem eventos
                break
                
        return eventos 