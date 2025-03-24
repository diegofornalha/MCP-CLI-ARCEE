#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente para API da Arcee

Este módulo implementa um cliente para a API da Arcee que permite
enviar prompts e receber respostas dos modelos da Arcee AI, como
alternativa aos modelos do Gemini.
"""

import requests
import json
import os
import logging
import time
import sys
from typing import Dict, List, Any, Optional, Union, Tuple
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,  # Alterado para DEBUG para mais detalhes
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("arcee_client")

# Carrega variáveis de ambiente
load_dotenv()

class ArceeClient:
    """Cliente para integração com a API da Arcee"""

    def __init__(self, api_key: Optional[str] = None, model: str = "auto"):
        """
        Inicializa o cliente Arcee
        
        Args:
            api_key (str, optional): Chave API da Arcee. Se None, usa a variável ARCEE_API_KEY
            model (str, optional): Modelo a ser usado. Padrão é "auto" para seleção automática
        """
        self.api_key = api_key or os.getenv("ARCEE_API_KEY")
        logger.debug(f"Verificando API key - presente: {bool(self.api_key)}")
        
        if not self.api_key:
            raise ValueError("API key não encontrada. Defina ARCEE_API_KEY no .env ou passe como parâmetro.")
        
        self.api_url = "https://models.arcee.ai/v1/chat/completions"
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Mensagem do sistema solicitando respostas em português
        self.system_message = {
            "role": "system", 
            "content": "Você deve sempre responder em português do Brasil. O usuário se chama Diego. Use uma linguagem natural e informal, mas profissional. Suas respostas devem ser claras, objetivas e culturalmente adequadas para o Brasil."
        }
        
        logger.info(f"Cliente Arcee inicializado com modelo: {model}")
        logger.debug(f"API URL: {self.api_url}")
        logger.debug(f"Headers configurados (sem exibir a chave completa): Content-Type: {self.headers['Content-Type']}, Authorization: Bearer {self.api_key[:5]}...")

    def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Gera conteúdo com um modelo da Arcee
        
        Args:
            prompt (str): O prompt de texto para enviar ao modelo
            **kwargs: Argumentos adicionais para personalizar a requisição
            
        Returns:
            Dict[str, Any]: Resposta da API com o conteúdo gerado
        """
        # Configuração do payload
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        payload = {
            "model": self.model,
            "messages": [
                self.system_message,
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        logger.debug(f"Enviando prompt para a API da Arcee: {prompt[:100]}...")
        
        # Tentativas e backoff exponencial
        max_retries = kwargs.get("max_retries", 3)
        base_delay = kwargs.get("base_delay", 1)
        
        for attempt in range(max_retries):
            try:
                # Faz a requisição para a API
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    data=json.dumps(payload),
                    timeout=kwargs.get("timeout", 30)
                )
                
                # Verifica se a requisição foi bem-sucedida
                response.raise_for_status()
                
                # Processa e retorna a resposta
                result = self._process_response(response.json())
                logger.debug(f"Resposta recebida da API da Arcee: {result['text'][:100]}...")
                return result
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentativa {attempt+1}/{max_retries} falhou: {e}")
                if hasattr(e, 'response') and e.response:
                    logger.warning(f"Detalhes: {e.response.text}")
                
                if attempt < max_retries - 1:
                    # Backoff exponencial
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Aguardando {delay}s antes de tentar novamente...")
                    time.sleep(delay)
                else:
                    logger.error(f"Erro final na chamada à API da Arcee: {e}")
                    return {"error": str(e)}
    
    def _process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa a resposta da API da Arcee
        
        Args:
            response_data (Dict[str, Any]): Dados da resposta da API
            
        Returns:
            Dict[str, Any]: Resposta processada
        """
        try:
            # Extrai o texto da resposta
            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Obtém metadados da resposta
            finish_reason = response_data.get("choices", [{}])[0].get("finish_reason", "")
            model_used = response_data.get("model", "unknown")
            
            # Verifica se há informações sobre o modelo selecionado pelo router
            model_selection = response_data.get("model_selection", {})
            selected_model = model_selection.get("selected_model", model_used)
            selection_reason = model_selection.get("reason", "")
            task_type = model_selection.get("task_type", "")
            domain = model_selection.get("domain", "")
            complexity = model_selection.get("complexity", "")
            
            # Formata a resposta
            processed_response = {
                "text": content,
                "finish_reason": finish_reason,
                "model": model_used,
                "selected_model": selected_model,
                "selection_reason": selection_reason,
                "task_type": task_type,
                "domain": domain,
                "complexity": complexity,
                "raw_response": response_data
            }
            
            return processed_response
        
        except (KeyError, IndexError) as e:
            logger.error(f"Erro ao processar resposta da Arcee: {e}")
            logger.error(f"Resposta recebida: {response_data}")
            return {
                "text": "",
                "error": f"Falha ao processar resposta: {str(e)}",
                "raw_response": response_data
            }

    def generate_content_chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Gera conteúdo no formato de chat com um modelo da Arcee
        
        Args:
            messages (List[Dict[str, str]]): Lista de mensagens no formato de chat
            **kwargs: Argumentos adicionais para personalizar a requisição
            
        Returns:
            Dict[str, Any]: Resposta da API com o conteúdo gerado
        """
        # Configuração do payload
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        # Adiciona a mensagem do sistema no início se não estiver presente
        if not messages or messages[0].get("role") != "system":
            messages = [self.system_message] + messages
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        logger.debug(f"Enviando chat para a API da Arcee com {len(messages)} mensagens...")
        
        # Tentativas e backoff exponencial
        max_retries = kwargs.get("max_retries", 3)
        base_delay = kwargs.get("base_delay", 1)
        
        for attempt in range(max_retries):
            try:
                # Faz a requisição para a API
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    data=json.dumps(payload),
                    timeout=kwargs.get("timeout", 30)
                )
                
                # Verifica se a requisição foi bem-sucedida
                response.raise_for_status()
                
                # Processa e retorna a resposta
                result = self._process_response(response.json())
                logger.debug(f"Resposta de chat recebida da API da Arcee: {result['text'][:100]}...")
                return result
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentativa de chat {attempt+1}/{max_retries} falhou: {e}")
                if hasattr(e, 'response') and e.response:
                    logger.warning(f"Detalhes: {e.response.text}")
                
                if attempt < max_retries - 1:
                    # Backoff exponencial
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Aguardando {delay}s antes de tentar novamente...")
                    time.sleep(delay)
                else:
                    logger.error(f"Erro final na chamada de chat à API da Arcee: {e}")
                    return {"error": str(e)}

    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Gera conteúdo no formato de chat com streaming
        
        Args:
            messages (List[Dict[str, str]]): Lista de mensagens no formato de chat
            **kwargs: Argumentos adicionais para personalizar a requisição
            
        Yields:
            str: Fragmentos de texto gerados pelo modelo
        """
        # Configuração do payload
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        # Adiciona a mensagem do sistema no início se não estiver presente
        if not messages or messages[0].get("role") != "system":
            messages = [self.system_message] + messages
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True  # Habilita streaming
        }
        
        logger.debug(f"Iniciando streaming de chat com a API da Arcee...")
        
        try:
            # Faz a requisição para a API
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=kwargs.get("timeout", 60)
            )
            
            # Verifica se a requisição foi bem-sucedida
            response.raise_for_status()
            
            # Processa a resposta streamed
            full_text = ""
            for line in response.iter_lines():
                if line:
                    # Remove o prefixo 'data: ' e processa o JSON
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        json_str = line_text[6:]  # Remove o prefixo 'data: '
                        
                        # '[DONE]' indica o fim do streaming
                        if json_str == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(json_str)
                            delta = chunk.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                full_text += content
                                yield content
                        except json.JSONDecodeError:
                            logger.warning(f"Falha ao decodificar JSON: {json_str}")
            
            # Retorna o texto completo no final
            return {"text": full_text, "model": self.model}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro no streaming de chat com a API da Arcee: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Detalhes: {e.response.text}")
            return {"error": str(e)}

    def get_available_models(self) -> List[str]:
        """
        Retorna uma lista dos modelos disponíveis na Arcee
        
        Returns:
            List[str]: Lista de modelos disponíveis
        """
        # Modelos conhecidos da Arcee
        return [
            "auto",            # Seleção automática pelo router
            "virtuoso-small",
            "virtuoso-medium",
            "virtuoso-large",
            "coder-small",
            "coder-large",
            "caller-large",
            "blitz"
        ]
    
    def set_system_message(self, content: str) -> None:
        """
        Define uma nova mensagem do sistema
        
        Args:
            content (str): Conteúdo da mensagem do sistema
        """
        self.system_message = {"role": "system", "content": content}
        logger.info("Mensagem do sistema atualizada")
    
    def health_check(self) -> Tuple[bool, str]:
        """
        Verifica se a API da Arcee está respondendo
        
        Returns:
            Tuple[bool, str]: (status, mensagem)
        """
        try:
            logger.debug("Iniciando health check da API Arcee")
            # Faz uma chamada simples para verificar se a API está funcionando
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "max_tokens": 5
            }
            
            logger.debug(f"Enviando payload para health check: {json.dumps(payload)}")
            logger.debug(f"URL: {self.api_url}")
            logger.debug(f"Headers (parcial): {{'Content-Type': '{self.headers['Content-Type']}', 'Authorization': 'Bearer {self.api_key[:5]}...'}}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=5
            )
            
            logger.debug(f"Resposta recebida - Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    logger.debug(f"Resposta JSON: {json.dumps(resp_json)[:200]}...")
                    return True, "API da Arcee está respondendo normalmente"
                except Exception as je:
                    logger.error(f"Erro ao decodificar JSON da resposta: {je}")
                    logger.debug(f"Conteúdo da resposta: {response.text[:200]}...")
                    return False, f"Erro ao processar resposta da API: {str(je)}"
            else:
                logger.error(f"API respondeu com status de erro: {response.status_code}")
                logger.debug(f"Conteúdo da resposta de erro: {response.text[:500]}")
                return False, f"API da Arcee respondeu com status {response.status_code}: {response.text}"
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição durante health check: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Detalhes da resposta de erro: {e.response.text[:500]}")
            return False, f"Erro ao conectar com a API da Arcee: {str(e)}"
        except Exception as e:
            logger.error(f"Erro inesperado durante health check: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False, f"Erro inesperado: {str(e)}"

# Exemplo de uso
if __name__ == "__main__":
    client = ArceeClient()
    response = client.generate_content("Explique como fazer uma integração de API em Python")
    print(response["text"])
    
    # Se o modo auto foi usado, exibe informações sobre a seleção
    if response.get("selected_model"):
        print(f"\nModelo selecionado: {response.get('selected_model')}")
        print(f"Razão da seleção: {response.get('selection_reason')}")
        print(f"Tipo de tarefa: {response.get('task_type')}")
        print(f"Domínio: {response.get('domain')}")
        print(f"Complexidade: {response.get('complexity')}")
