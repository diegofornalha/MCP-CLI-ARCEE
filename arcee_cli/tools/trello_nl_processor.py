#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Processador de Linguagem Natural para o Trello

Este módulo intercepta comandos em linguagem natural relacionados ao Trello
durante o chat e os traduz em ações do Trello.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
import os
import requests
from datetime import datetime

# Configuração de logging
logger = logging.getLogger("trello_nl_processor")

class TrelloNLProcessor:
    """
    Processador de comandos em linguagem natural para o Trello.
    
    Esta classe detecta e processa comandos em linguagem natural relacionados
    ao Trello durante o chat e executa as ações correspondentes.
    """
    
    def __init__(self, agent=None):
        """
        Inicializa o processador
        
        Args:
            agent: Agente para executar comandos do Trello
        """
        self.agent = agent
        
        # Armazena quadros pendentes de exclusão (ID => nome)
        self.quadros_pendentes_exclusao = {}
        
        # Cache para armazenar informações temporariamente e reduzir chamadas à API
        self.cache = {
            'boards': {'data': None, 'timestamp': 0},
            'lists': {}, # formato: {'board_id': {'data': [...], 'timestamp': 0}}
            'cards': {}  # formato: {'list_id': {'data': [...], 'timestamp': 0}}
        }
        
        # Tempo máximo de validade do cache em segundos (5 minutos por padrão)
        self.cache_ttl = 300
        
        # Padrões para comandos comuns do Trello
        self.comandos_padroes = [
            # Listar quadros
            (r'(mostrar?|exibir?|listar?|ver?)\s+(os\s+)?(quadros|boards?)(\s+do\s+trello)?', 'listar_quadros'),
            
            # Listar listas
            (r'(mostrar?|exibir?|listar?|ver?)\s+(as\s+)?listas(\s+do\s+trello)?(\s+do\s+quadro)?(\s+com\s+id)?(\s+com\s+url)?', 'listar_listas'),
            
            # Listar cards
            (r'(mostrar?|exibir?|listar?|ver?)\s+(os\s+)?(cards?|cartões|tarefas)(\s+do\s+trello)?(\s+da\s+lista)?', 'listar_cards'),
            
            # Criar lista
            (r'(criar?|adicionar?|nova)\s+(uma\s+)?lista(\s+no\s+trello)?(\s+com\s+nome|\s+chamada)?', 'criar_lista'),
            
            # Criar card
            (r'(criar?|adicionar?|novo)\s+(um\s+)?(card|cartão|tarefa)(\s+no\s+trello)?(\s+na\s+lista)?', 'criar_card'),
            
            # Arquivar card
            (r'(arquivar?|remover?|excluir?)\s+(um\s+)?(card|cartão|tarefa)(\s+do\s+trello)?', 'arquivar_card'),
            
            # Atividade
            (r'(mostrar?|exibir?|listar?|ver?)\s+(as\s+)?atividades?(\s+do\s+trello)?', 'listar_atividade'),
            
            # Criar quadro
            (r'(criar?|adicionar?|novo)\s+(um\s+)?quadro(\s+no\s+trello)?(\s+com\s+nome|\s+chamado)?', 'criar_quadro'),
            
            # Apagar quadro
            (r'(apagar?|deletar?|excluir?|remover?)\s+(um\s+)?quadro(\s+do\s+trello)?(\s+com\s+id|\s+com\s+url)?', 'apagar_quadro'),
            
            # Buscar card
            (r'(buscar?|localizar?|encontrar?|achar?|procurar?)\s+(um\s+)?(card|cartão|tarefa)(\s+do\s+trello)?(\s+com\s+nome)?(\s+chamado)?', 'buscar_card'),
            
            # Confirmação (sim, confirmar, etc.)
            (r'^(sim|s|yes|y|confirmar|confirmo|pode|concordo)$', 'confirmar'),
        ]
        
    def detectar_comando(self, mensagem: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Detecta se uma mensagem contém um comando do Trello
        
        Args:
            mensagem: Mensagem do usuário
            
        Returns:
            Tupla com (é_comando, tipo_comando, parametros)
        """
        # Converte para minúsculas para facilitar a detecção
        texto = mensagem.lower()
        
        # Verifica se é uma confirmação para quadros pendentes
        if texto.strip() in ["sim", "s", "yes", "y", "confirmar", "confirmo", "pode", "concordo"] and self.quadros_pendentes_exclusao:
            return True, 'confirmar', {}
        
        # Verifica se a mensagem menciona o Trello
        if 'trello' not in texto and not any(termo in texto for termo in ['card', 'cartão', 'lista', 'tarefa', 'quadro']):
            return False, None, {}
            
        # Tenta identificar o comando
        for padrao, tipo_comando in self.comandos_padroes:
            match = re.search(padrao, texto)
            if match:
                # Extrai parâmetros baseados no tipo de comando
                params = self._extrair_parametros(texto, tipo_comando)
                return True, tipo_comando, params
                
        # Se chegou até aqui, não identificou um comando específico
        return True, 'comando_desconhecido', {'texto_original': mensagem}
        
    def _extrair_parametros(self, texto: str, tipo_comando: str) -> Dict[str, Any]:
        """
        Extrai parâmetros de um comando em texto
        
        Args:
            texto: Texto do comando
            tipo_comando: Tipo do comando detectado
            
        Returns:
            Dicionário com parâmetros extraídos
        """
        params = {}
        
        if tipo_comando == 'listar_cards':
            # Tenta extrair o nome da lista
            match_lista = re.search(r'(?:da|na|do|no|para a|para o)\s+lista\s+(?:chamada\s+|com\s+nome\s+)?["\']?([^"\']+)["\']?', texto)
            if match_lista:
                params['lista_nome'] = match_lista.group(1).strip()
        
        elif tipo_comando == 'listar_listas':
            # Tenta extrair o ID ou URL do quadro
            match_quadro_id = re.search(r'(?:quadro|board)\s+(?:com\s+id|id)\s+["\']?([A-Za-z0-9]+)["\']?', texto)
            match_quadro_url = re.search(r'(?:quadro|board)\s+(?:com\s+url|url)\s+["\']?(https?://trello\.com/b/[A-Za-z0-9]+(?:/[^"\']*)?)["\']?', texto)
            
            if match_quadro_id:
                params['quadro_id'] = match_quadro_id.group(1).strip()
            elif match_quadro_url:
                url = match_quadro_url.group(1).strip()
                # Extrai o ID do quadro da URL
                match_id = re.search(r'trello\.com/b/([^/]+)', url)
                if match_id:
                    params['quadro_id'] = match_id.group(1)
                params['quadro_url'] = url
                
        elif tipo_comando == 'buscar_card':
            # Tenta extrair o nome do card a buscar
            nome_card_patterns = [
                r'(?:chamado|com\s+nome)\s+["\']?([^"\']+)["\']?',
                r'(?:card|cartão|tarefa)\s+["\']?([^"\']+)["\']?',
                r'(?:buscar|localizar|encontrar|achar|procurar)[^"\']*["\']([^"\']+)["\']'
            ]
            
            card_nome = None
            for pattern in nome_card_patterns:
                match = re.search(pattern, texto)
                if match:
                    card_nome = match.group(1).strip()
                    break
                    
            if card_nome:
                params['card_nome'] = card_nome
                
            # Tenta extrair o ID ou nome do quadro específico
            match_quadro_id = re.search(r'(?:quadro|board)\s+(?:com\s+id|id)\s+["\']?([A-Za-z0-9]+)["\']?', texto)
            match_quadro_nome = re.search(r'(?:quadro|board)\s+(?:chamado|com\s+nome)\s+["\']?([^"\']+)["\']?', texto)
            match_quadro_url = re.search(r'(?:quadro|board)\s+(?:com\s+url|url)\s+["\']?(https?://trello\.com/b/[A-Za-z0-9]+(?:/[^"\']*)?)["\']?', texto)
            
            if match_quadro_id:
                params['quadro_id'] = match_quadro_id.group(1).strip()
            elif match_quadro_nome:
                params['quadro_nome'] = match_quadro_nome.group(1).strip()
            elif match_quadro_url:
                url = match_quadro_url.group(1).strip()
                # Extrai o ID do quadro da URL
                match_id = re.search(r'trello\.com/b/([^/]+)', url)
                if match_id:
                    params['quadro_id'] = match_id.group(1)
                params['quadro_url'] = url
        
        elif tipo_comando == 'criar_lista':
            # Tenta extrair o nome da lista
            match_nome = re.search(r'(?:chamada|com\s+nome|nome)\s+["\']?([^"\']+)["\']?', texto)
            if match_nome:
                params['nome'] = match_nome.group(1).strip()
            else:
                # Procura por qualquer texto após "criar lista" ou similar
                match_nome = re.search(r'(?:criar|adicionar|nova)\s+(?:uma\s+)?lista\s+["\']?([^"\']+)["\']?', texto)
                if match_nome:
                    params['nome'] = match_nome.group(1).strip()
        
        elif tipo_comando == 'criar_card':
            # Tenta extrair o nome da lista (mais variações)
            match_lista = None
            lista_patterns = [
                r'(?:na|no|da|do)\s+lista\s+(?:chamada\s+|com\s+nome\s+)?["\']?([^"\']+)["\']?',
                r'(?:na|no|da|do)\s+lista\s+([A-Za-z0-9]+)',
                r'lista\s+(?:chamada\s+|com\s+nome\s+)?["\']?([^"\']+)["\']?',
                r'em\s+["\']?([^"\']+)["\']?'
            ]
            
            for pattern in lista_patterns:
                match_lista = re.search(pattern, texto)
                if match_lista:
                    params['lista_nome'] = match_lista.group(1).strip()
                    break
                
            # Tenta extrair o nome do card (mais variações)
            match_nome = None
            nome_patterns = [
                r'(?:chamado|com\s+nome|nome|título)\s+["\']?([^"\']+)["\']?',
                r'card\s+["\']?([^"\']+)["\']?',
                r'cartão\s+["\']?([^"\']+)["\']?',
                r'tarefa\s+["\']?([^"\']+)["\']?',
                r'(?:criar|adicionar|novo)\s+(?:um\s+)?(?:card|cartão|tarefa)\s+["\']?([^"\']+)["\']?'
            ]
            
            for pattern in nome_patterns:
                match_nome = re.search(pattern, texto)
                if match_nome:
                    nome_extraido = match_nome.group(1).strip()
                    # Verifica se o que foi extraído tem "na lista" - se tiver, precisamos extrair só o nome
                    na_lista_match = re.search(r'(.*?)\s+(?:na|no|da|do)\s+lista', nome_extraido)
                    if na_lista_match:
                        nome_extraido = na_lista_match.group(1).strip()
                    params['nome'] = nome_extraido
                    break
                
            # Tenta extrair a descrição
            match_desc = re.search(r'(?:descrição|com\s+descrição)\s+["\']?([^"\']+)["\']?', texto)
            if match_desc:
                params['descricao'] = match_desc.group(1).strip()
                
            # Procura por outros possíveis detalhes
            match_quadro = re.search(r'(?:quadro|board)\s+(?:chamado\s+|com\s+nome\s+)?["\']?([^"\']+)["\']?', texto)
            if match_quadro:
                params['quadro_nome'] = match_quadro.group(1).strip()
                
            # Tenta detectar uma possível data de vencimento
            match_data = re.search(r'(?:vencimento|data|até|prazo)\s+(?:para\s+|de\s+)?["\']?([0-9]{1,2}[-/][0-9]{1,2}(?:[-/][0-9]{2,4})?)["\']?', texto)
            if match_data:
                params['data_vencimento'] = match_data.group(1).strip()
        
        elif tipo_comando == 'arquivar_card':
            # Tenta extrair o nome ou ID do card
            match_card = re.search(r'(?:card|cartão|tarefa)\s+(?:chamado|com\s+nome|nome|título)\s+["\']?([^"\']+)["\']?', texto)
            if match_card:
                params['card_nome'] = match_card.group(1).strip()
        
        elif tipo_comando == 'listar_atividade':
            # Tenta extrair o limite
            match_limite = re.search(r'(?:últimas|últimos|limite)\s+(\d+)', texto)
            if match_limite:
                try:
                    params['limite'] = int(match_limite.group(1))
                except:
                    pass
                    
        elif tipo_comando == 'criar_quadro':
            # Tenta extrair o nome do quadro
            match_nome = re.search(r'(?:chamado|com\s+nome|nome)\s+["\']?([^"\']+)["\']?', texto)
            if match_nome:
                params['nome'] = match_nome.group(1).strip()
            else:
                # Procura por qualquer texto após "criar quadro" ou similar
                match_nome = re.search(r'(?:criar|adicionar|novo)\s+(?:um\s+)?quadro\s+["\']?([^"\']+)["\']?', texto)
                if match_nome:
                    params['nome'] = match_nome.group(1).strip()
                    
            # Tenta extrair a descrição
            match_desc = re.search(r'(?:descrição|com\s+descrição)\s+["\']?([^"\']+)["\']?', texto)
            if match_desc:
                params['descricao'] = match_desc.group(1).strip()
                
        elif tipo_comando == 'apagar_quadro':
            # Tenta extrair URL ou ID do quadro
            match_url = re.search(r'(?:url|link)\s+["\']?(https?://trello\.com/b/[^"\']+)["\']?', texto)
            if match_url:
                params['quadro_url'] = match_url.group(1).strip()
            else:
                # Tenta encontrar uma URL no texto
                match_url = re.search(r'(https?://trello\.com/b/[^\s]+)', texto)
                if match_url:
                    params['quadro_url'] = match_url.group(1).strip()
                else:
                    # Tenta extrair o ID diretamente
                    match_id = re.search(r'(?:id|identificador)\s+["\']?([a-zA-Z0-9]+)["\']?', texto)
                    if match_id:
                        params['quadro_id'] = match_id.group(1).strip()
        
        return params
    
    def processar_comando(self, tipo_comando: str, params: Dict[str, Any]) -> Optional[str]:
        """
        Processa um comando do Trello
        
        Args:
            tipo_comando: Tipo de comando a processar
            params: Parâmetros do comando
            
        Returns:
            Resposta do comando ou None se não foi possível processar
        """
        if not self.agent and tipo_comando not in ['listar_listas', 'criar_card', 'listar_quadros', 'criar_quadro', 'apagar_quadro', 'confirmar', 'buscar_card']:
            return "❌ Agente não disponível para processar comandos do Trello"
            
        try:
            if tipo_comando == 'listar_quadros':
                return self._comando_listar_quadros()
            
            elif tipo_comando == 'listar_listas':
                return self._comando_listar_listas(params)
            
            elif tipo_comando == 'listar_cards':
                return self._comando_listar_cards(params)
                
            elif tipo_comando == 'criar_lista':
                return self._comando_criar_lista(params)
                
            elif tipo_comando == 'criar_card':
                return self._comando_criar_card(params)
                
            elif tipo_comando == 'arquivar_card':
                return self._comando_arquivar_card(params)
                
            elif tipo_comando == 'listar_atividade':
                return self._comando_listar_atividade(params)
                
            elif tipo_comando == 'criar_quadro':
                return self._comando_criar_quadro(params)
                
            elif tipo_comando == 'apagar_quadro':
                return self._comando_apagar_quadro(params)
                
            elif tipo_comando == 'buscar_card':
                return self._comando_buscar_card(params)
                
            elif tipo_comando == 'confirmar':
                return self._comando_confirmar()
                
            elif tipo_comando == 'comando_desconhecido':
                # Retorna None para permitir que o LLM processe a mensagem
                # Em vez de mostrar uma mensagem genérica
                return None
            
            return None
            
        except Exception as e:
            logger.exception(f"Erro ao processar comando do Trello: {e}")
            return f"❌ Erro ao processar comando do Trello: {str(e)}"
    
    def _comando_listar_quadros(self) -> str:
        """Processa o comando para listar quadros"""
        import requests
        import os
        
        # Obtém as credenciais do Trello
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            return "❌ Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
            
        # Verifica se tem dados em cache
        quadros = self._get_from_cache('boards')
        
        if quadros is None:
            try:
                # Parâmetros para a requisição
                params = {
                    "key": api_key,
                    "token": token
                }
                
                # Faz a requisição para obter os quadros
                response = requests.get("https://api.trello.com/1/members/me/boards", params=params)
                response.raise_for_status()
                
                quadros = response.json()
                
                # Armazena no cache
                self._store_in_cache('boards', quadros)
                
            except requests.exceptions.RequestException as e:
                erro = f"❌ Erro ao listar quadros: {str(e)}"
                if hasattr(e, 'response') and e.response:
                    erro += f"\nResposta: {e.response.text}"
                return erro
        
        # Formata os quadros em texto
        if not quadros:
            return "ℹ️ Você não tem nenhum quadro no Trello."
            
        result = "📋 Seus Quadros no Trello:\n\n"
        
        for i, quadro in enumerate(quadros, 1):
            result += f"{i}. {quadro.get('name', 'N/A')}\n"
            result += f"   ID: {quadro.get('id', 'N/A')}\n"
            result += f"   URL: {quadro.get('url', 'N/A')}\n\n"
            
        return result.strip()
    
    def _comando_listar_listas(self, params: Optional[Dict[str, Any]] = None) -> str:
        """Processa o comando para listar listas"""
        import requests
        import os
        
        if params is None:
            params = {}
            
        board_id = params.get('board_id')
        board_url = params.get('board_url')
        quadro_de_referencia = ""
        
        # Obtém as credenciais do Trello
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            return "❌ Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
        
        # Se recebemos uma URL do quadro, extraímos o ID
        if board_url and not board_id:
            try:
                # Extrai o ID do quadro da URL
                url_parts = board_url.split("/")
                for i, part in enumerate(url_parts):
                    if part == "b" and i + 1 < len(url_parts):
                        board_id = url_parts[i+1].split("/")[0]
                        break
                if not board_id:
                    return f"❌ Não foi possível extrair o ID do quadro da URL: {board_url}"
                    
                quadro_de_referencia = f"quadro com URL {board_url}"
            except Exception as e:
                return f"❌ Erro ao extrair ID do quadro da URL: {e}"
                
        # Se ainda não temos o ID do quadro, usamos o padrão do .env
        if not board_id:
            board_id = os.getenv("TRELLO_BOARD_ID")
            if not board_id:
                return "❌ ID do quadro não encontrado. Especifique um quadro ou configure TRELLO_BOARD_ID no arquivo .env."
            quadro_de_referencia = "quadro padrão"
        else:
            quadro_de_referencia = f"quadro {board_id}"
        
        # Verifica se tem dados em cache
        listas = self._get_from_cache('lists', board_id=board_id)
        
        # Se não tem no cache, busca da API
        if listas is None:
            try:
                # Parâmetros para a requisição
                request_params = {
                    "key": api_key,
                    "token": token
                }
                
                # Faz a requisição para obter as listas
                response = requests.get(f"https://api.trello.com/1/boards/{board_id}/lists", params=request_params)
                response.raise_for_status()
                
                listas = response.json()
                
                # Armazena no cache
                self._store_in_cache('lists', listas, board_id=board_id)
                
            except requests.exceptions.RequestException as e:
                erro = f"❌ Erro ao listar listas: {str(e)}"
                if hasattr(e, 'response') and e.response:
                    erro += f"\nResposta: {e.response.text}"
                return erro
        
        if not listas:
            return f"ℹ️ Nenhuma lista encontrada no {quadro_de_referencia}."
            
        # Formata as listas em texto
        result = f"📋 Listas do {quadro_de_referencia}:\n\n"
        
        for i, lista in enumerate(listas, 1):
            # Para cada lista, obtém o número de cards (usando cache se disponível)
            cards = self._get_from_cache('cards', list_id=lista['id'])
            
            if cards is None:
                try:
                    cards_response = requests.get(f"https://api.trello.com/1/lists/{lista['id']}/cards", 
                                               params={"key": api_key, "token": token})
                    cards_response.raise_for_status()
                    cards = cards_response.json()
                    
                    # Armazena no cache
                    self._store_in_cache('cards', cards, list_id=lista['id'])
                except:
                    # Se falhar, apenas continua sem o número de cards
                    cards = []
            
            result += f"{i}. {lista.get('name', 'N/A')} (ID: {lista.get('id', 'N/A')}) - {len(cards)} cards\n"
            
        return result
    
    def _comando_listar_cards(self, params: Dict[str, Any]) -> str:
        """Processa o comando para listar cards"""
        import requests
        import os
        
        lista_nome = params.get('lista_nome')
        lista_id = params.get('lista_id')
        
        # Obtém as credenciais do Trello
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            return "❌ Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
        
        # Parâmetros comuns para requisições
        auth_params = {
            "key": api_key,
            "token": token
        }
        
        try:
            # Se temos um ID de lista, usamos diretamente
            if lista_id:
                # Obtém informações da lista para mostrar o nome
                lista_url = f"https://api.trello.com/1/lists/{lista_id}"
                lista_response = requests.get(lista_url, params=auth_params)
                
                lista_nome_exibir = lista_id
                if lista_response.status_code == 200:
                    lista_info = lista_response.json()
                    lista_nome_exibir = lista_info.get("name", lista_id)
                
                # Obtém os cards da lista
                cards_url = f"https://api.trello.com/1/lists/{lista_id}/cards"
                cards_response = requests.get(cards_url, params=auth_params)
                
                if cards_response.status_code != 200:
                    return f"❌ Erro ao obter cards da lista: {cards_response.status_code}\nResposta: {cards_response.text}"
                
                cards = cards_response.json()
                
                return self._formatar_cards_resultado(cards, lista_nome_exibir)
                
            # Se temos um nome de lista, precisamos primeiro encontrar o ID
            elif lista_nome:
                # Obtém todas as listas para encontrar a que corresponde ao nome
                boards_url = "https://api.trello.com/1/members/me/boards"
                boards_response = requests.get(boards_url, params=auth_params)
                
                if boards_response.status_code != 200:
                    return f"❌ Erro ao obter quadros: {boards_response.status_code}\nResposta: {boards_response.text}"
                
                boards = boards_response.json()
                
                if not boards:
                    return "❌ Nenhum quadro encontrado para buscar listas."
                
                # Busca em todas as listas de todos os quadros
                for board in boards:
                    board_id = board.get("id")
                    lists_url = f"https://api.trello.com/1/boards/{board_id}/lists"
                    lists_response = requests.get(lists_url, params=auth_params)
                    
                    if lists_response.status_code != 200:
                        continue  # Pula para o próximo quadro se houver erro
                    
                    lists = lists_response.json()
                    
                    # Procura lista pelo nome (case insensitive)
                    for lst in lists:
                        if lista_nome.lower() in lst.get("name", "").lower():
                            lista_id = lst.get("id")
                            lista_nome_exibir = lst.get("name")
                            
                            # Obtém os cards da lista
                            cards_url = f"https://api.trello.com/1/lists/{lista_id}/cards"
                            cards_response = requests.get(cards_url, params=auth_params)
                            
                            if cards_response.status_code != 200:
                                return f"❌ Erro ao obter cards da lista: {cards_response.status_code}\nResposta: {cards_response.text}"
                            
                            cards = cards_response.json()
                            
                            return self._formatar_cards_resultado(cards, lista_nome_exibir)
                
                return f"❌ Lista '{lista_nome}' não encontrada. Verifique o nome e tente novamente."
            
            # Se não há nome nem ID, pede para especificar
            else:
                return "❌ Por favor, especifique o nome ou ID da lista para mostrar os cards."
                
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Erro ao acessar a API do Trello: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f"\nResposta: {e.response.text}"
            logger.exception(error_msg)
            return error_msg
        
        except Exception as e:
            error_msg = f"❌ Erro inesperado: {str(e)}"
            logger.exception(error_msg)
            return error_msg
    
    def _formatar_cards_resultado(self, cards: List[Dict], lista_nome: str) -> str:
        """Formata a resposta com os cards"""
        if not cards:
            return f"ℹ️ A lista '{lista_nome}' não possui cards."
        
        resposta = f"📋 Cards na lista '{lista_nome}' ({len(cards)} encontrados):\n\n"
        
        for i, card in enumerate(cards, 1):
            nome = card.get("name", "Sem nome")
            desc = card.get("desc", "")
            url = card.get("shortUrl", "")
            
            resposta += f"{i}. {nome}\n"
            if url:
                resposta += f"   URL: {url}\n"
            if desc:
                # Limita a descrição a 100 caracteres
                desc_preview = desc[:100] + "..." if len(desc) > 100 else desc
                resposta += f"   Descrição: {desc_preview}\n"
            resposta += "\n"
        
        return resposta.strip()
    
    def _comando_criar_lista(self, params: Dict[str, Any]) -> str:
        """Processa o comando para criar uma lista"""
        if not self.agent:
            return "❌ Agente não disponível para processar comandos do Trello"
            
        nome = params.get('nome')
        
        if not nome:
            return "❌ Nome da lista não especificado. Por favor, informe o nome da lista que deseja criar."
            
        response = self.agent.run_tool("add_list_to_board", {"name": nome})
        
        if "error" in response:
            return f"❌ Erro: {response['error']}"
            
        return f"✅ Lista '{nome}' criada com sucesso! (ID: {response.get('id')})"
    
    def _comando_criar_card(self, params: Dict[str, Any]) -> str:
        """Processa o comando para criar um card"""
        import requests
        import os
        
        # Verifica se temos o nome do card
        nome = params.get('nome')
        if not nome:
            return "❌ Nome do card não especificado. Por favor, informe o nome do card que deseja criar."
        
        # Obtém a lista onde o card será criado
        lista_nome = params.get('lista_nome')
        lista_id = params.get('lista_id')
        quadro_nome = params.get('quadro_nome')
        
        # Obtém as credenciais do Trello
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            return "❌ Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
        
        # Parâmetros comuns para requisições
        auth_params = {
            "key": api_key,
            "token": token
        }
        
        try:
            # Se temos um nome de quadro específico, tentamos encontrá-lo primeiro
            board_id = None
            if quadro_nome:
                # Verifica se temos os quadros em cache
                quadros = self._get_from_cache('boards')
                
                if quadros is None:
                    # Obtém todos os quadros
                    boards_response = requests.get("https://api.trello.com/1/members/me/boards", params=auth_params)
                    
                    if boards_response.status_code != 200:
                        return f"❌ Erro ao obter quadros: {boards_response.status_code}\nResposta: {boards_response.text}"
                    
                    quadros = boards_response.json()
                    self._store_in_cache('boards', quadros)
                    
                # Busca o quadro pelo nome
                for quadro in quadros:
                    if quadro_nome.lower() in quadro.get("name", "").lower():
                        board_id = quadro.get("id")
                        break
                
                if not board_id:
                    return f"❌ Quadro '{quadro_nome}' não encontrado. Verifique o nome e tente novamente."
            
            # Se não temos o ID da lista, mas temos o nome, precisamos encontrar o ID
            if not lista_id and lista_nome:
                # Se já temos um board_id específico, buscamos apenas nele
                if board_id:
                    # Verifica se temos as listas deste quadro em cache
                    listas = self._get_from_cache('lists', board_id=board_id)
                    
                    if listas is None:
                        # Obtém as listas do quadro
                        lists_url = f"https://api.trello.com/1/boards/{board_id}/lists"
                        lists_response = requests.get(lists_url, params=auth_params)
                        
                        if lists_response.status_code != 200:
                            return f"❌ Erro ao obter listas: {lists_response.status_code}\nResposta: {lists_response.text}"
                        
                        listas = lists_response.json()
                        self._store_in_cache('lists', listas, board_id=board_id)
                    
                    # Procura lista pelo nome (case insensitive)
                    for lst in listas:
                        if lista_nome.lower() in lst.get("name", "").lower():
                            lista_id = lst.get("id")
                            lista_nome_exibir = lst.get("name")
                            break
                    
                    if not lista_id:
                        return f"❌ Lista '{lista_nome}' não encontrada no quadro especificado. Verifique o nome e tente novamente."
                else:
                    # Se não temos um quadro específico, buscamos em todos os quadros
                    # Verifica se temos os quadros em cache
                    quadros = self._get_from_cache('boards')
                    
                    if quadros is None:
                        # Obtém todos os quadros
                        boards_url = "https://api.trello.com/1/members/me/boards"
                        boards_response = requests.get(boards_url, params=auth_params)
                        
                        if boards_response.status_code != 200:
                            return f"❌ Erro ao obter quadros: {boards_response.status_code}\nResposta: {boards_response.text}"
                        
                        quadros = boards_response.json()
                        self._store_in_cache('boards', quadros)
                    
                    if not quadros:
                        return "❌ Nenhum quadro encontrado. Não é possível criar o card."
                    
                    # Busca a lista em todos os quadros
                    for board in quadros:
                        board_id = board.get("id")
                        
                        # Verifica se temos as listas deste quadro em cache
                        listas = self._get_from_cache('lists', board_id=board_id)
                        
                        if listas is None:
                            lists_url = f"https://api.trello.com/1/boards/{board_id}/lists"
                            lists_response = requests.get(lists_url, params=auth_params)
                            
                            if lists_response.status_code != 200:
                                continue  # Pula para o próximo quadro se houver erro
                            
                            listas = lists_response.json()
                            self._store_in_cache('lists', listas, board_id=board_id)
                        
                        # Procura lista pelo nome (case insensitive)
                        for lst in listas:
                            if lista_nome.lower() in lst.get("name", "").lower():
                                lista_id = lst.get("id")
                                lista_nome_exibir = lst.get("name")
                                quadro_nome_encontrado = board.get("name")
                                break
                        
                        # Se encontrou a lista, interrompe a busca
                        if lista_id:
                            break
                    
                    if not lista_id:
                        return f"❌ Lista '{lista_nome}' não encontrada. Verifique o nome e tente novamente."
            
            # Se mesmo assim não temos um ID de lista, obtém a primeira lista disponível
            if not lista_id:
                # Verifica se temos os quadros em cache
                quadros = self._get_from_cache('boards')
                
                if quadros is None:
                    # Obtém o primeiro quadro
                    boards_url = "https://api.trello.com/1/members/me/boards"
                    boards_response = requests.get(boards_url, params=auth_params)
                    
                    if boards_response.status_code != 200:
                        return f"❌ Erro ao obter quadros: {boards_response.status_code}\nResposta: {boards_response.text}"
                    
                    quadros = boards_response.json()
                    self._store_in_cache('boards', quadros)
                
                if not quadros:
                    return "❌ Nenhum quadro encontrado. Não é possível criar o card."
                
                # Obtém o primeiro quadro
                board_id = quadros[0].get("id")
                
                # Verifica se temos as listas deste quadro em cache
                listas = self._get_from_cache('lists', board_id=board_id)
                
                if listas is None:
                    # Obtém as listas do quadro
                    lists_url = f"https://api.trello.com/1/boards/{board_id}/lists"
                    lists_response = requests.get(lists_url, params=auth_params)
                    
                    if lists_response.status_code != 200:
                        return f"❌ Erro ao obter listas: {lists_response.status_code}\nResposta: {lists_response.text}"
                    
                    listas = lists_response.json()
                    self._store_in_cache('lists', listas, board_id=board_id)
                
                if not listas:
                    return "❌ Nenhuma lista encontrada no quadro. Não é possível criar o card."
                
                lista_id = listas[0].get("id")
                lista_nome_exibir = listas[0].get("name")
                
                return f"⚠️ Nenhuma lista especificada. Para criar o card '{nome}' na lista '{lista_nome_exibir}', por favor confirme com 'sim'."
            
            # Verifica se já temos o nome da lista para exibição
            if not 'lista_nome_exibir' in locals():
                # Obtém o nome da lista para exibição
                lista_url = f"https://api.trello.com/1/lists/{lista_id}"
                lista_response = requests.get(lista_url, params=auth_params)
                
                lista_nome_exibir = lista_id
                if lista_response.status_code == 200:
                    lista_info = lista_response.json()
                    lista_nome_exibir = lista_info.get("name", lista_id)
            
            # Cria o card
            desc = params.get('descricao', '')
            
            card_data = {
                "name": nome,
                "idList": lista_id,
                "desc": desc,
                "key": api_key,
                "token": token
            }
            
            # Adiciona data de vencimento se fornecida
            data_vencimento = params.get('data_vencimento')
            if data_vencimento:
                try:
                    # Tenta converter para um formato ISO 8601
                    # Primeiro identifica o formato da data
                    if '/' in data_vencimento:
                        partes = data_vencimento.split('/')
                    elif '-' in data_vencimento:
                        partes = data_vencimento.split('-')
                    else:
                        raise ValueError("Formato de data não reconhecido")
                    
                    # Normaliza para formato yyyy-mm-dd
                    if len(partes) == 3:
                        # Se o ano for fornecido com 2 dígitos, adiciona 2000
                        if len(partes[2]) == 2:
                            partes[2] = '20' + partes[2]
                        data_iso = f"{partes[2]}-{partes[1]}-{partes[0]}"
                    else:  # Se apenas dia e mês, use o ano atual
                        ano_atual = datetime.now().year
                        data_iso = f"{ano_atual}-{partes[1]}-{partes[0]}"
                    
                    card_data["due"] = data_iso
                except Exception as e:
                    return f"❌ Erro ao processar data de vencimento: {str(e)}"
            
            # Feedback para o usuário durante o processo
            processo = f"🔄 Criando card '{nome}' na lista '{lista_nome_exibir}'..."
            print(processo)
            
            # Faz a requisição para criar o card
            card_url = "https://api.trello.com/1/cards"
            card_response = requests.post(card_url, data=card_data)
            
            if card_response.status_code != 200:
                return f"❌ Erro ao criar card: {card_response.status_code}\nResposta: {card_response.text}"
            
            card = card_response.json()
            
            # Formata a resposta de sucesso
            card_nome = card.get("name")
            card_url = card.get("shortUrl")
            
            resposta = f"✅ Card '{card_nome}' criado com sucesso na lista '{lista_nome_exibir}'!\n"
            if card_url:
                resposta += f"URL: {card_url}\n"
                
            # Se tinha data de vencimento, mostra
            if 'due' in card and card['due']:
                data_formatada = card['due'].split('T')[0]  # Remove a parte de hora
                resposta += f"Data de vencimento: {data_formatada}"
            
            return resposta
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Erro ao acessar a API do Trello: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f"\nResposta: {e.response.text}"
            logger.exception(error_msg)
            return error_msg
        
        except Exception as e:
            error_msg = f"❌ Erro inesperado: {str(e)}"
            logger.exception(error_msg)
            return error_msg
    
    def _comando_arquivar_card(self, params: Dict[str, Any]) -> str:
        """Processa o comando para arquivar um card"""
        if not self.agent:
            return "❌ Agente não disponível para processar comandos do Trello"
            
        card_nome = params.get('card_nome')
        
        if not card_nome:
            return "❌ Card não especificado. Por favor, informe qual card deseja arquivar."
            
        # Primeiro precisa obter o ID do card pelo nome
        # Para isso, obtém todas as listas e seus cards
        listas_response = self.agent.run_tool("get_lists", {"random_string": "dummy"})
        
        if "error" in listas_response:
            return f"❌ Erro: {listas_response['error']}"
            
        # Procura o card em todas as listas
        card_id = None
        card_nome_completo = None
        
        for lista in listas_response.get("lists", []):
            lista_id = lista.get("id")
            
            # Obtém os cards da lista
            cards_response = self.agent.run_tool("get_cards_by_list_id", {"listId": lista_id})
            
            if "error" not in cards_response:
                for card in cards_response.get("cards", []):
                    if card_nome.lower() in card.get('name', '').lower():
                        card_id = card.get('id')
                        card_nome_completo = card.get('name')
                        lista_nome = lista.get('name')
                        break
            
            if card_id:
                break
        
        if not card_id:
            return f"❌ Card '{card_nome}' não encontrado. Verifique o nome e tente novamente."
            
        # Arquiva o card
        response = self.agent.run_tool("archive_card", {"cardId": card_id})
        
        if "error" in response:
            return f"❌ Erro: {response['error']}"
            
        return f"✅ Card '{card_nome_completo}' da lista '{lista_nome}' arquivado com sucesso!"
    
    def _comando_listar_atividade(self, params: Dict[str, Any]) -> str:
        """Processa o comando para listar atividades"""
        if not self.agent:
            return "❌ Agente não disponível para processar comandos do Trello"
            
        limite = params.get('limite', 10)
        
        response = self.agent.run_tool("get_recent_activity", {"limit": limite})
        
        if "error" in response:
            return f"❌ Erro: {response['error']}"
            
        # Formata as atividades em texto
        result = f"📊 {limite} Atividades Recentes do Trello:\n\n"
        
        for atividade in response.get("actions", []):
            # Formata a data para exibição
            data = atividade.get("date", "N/A")
            # Simplifica para apenas a parte da data e hora
            if "T" in data:
                data = data.replace("T", " ").split(".")[0]
                
            usuario = atividade.get("memberCreator", {}).get("fullName", "N/A")
            acao = atividade.get("text", "N/A")
            
            result += f"• {data} - {usuario}: {acao}\n"
            
        return result
    
    def _comando_criar_quadro(self, params: Dict[str, Any]) -> str:
        """Processa o comando para criar um quadro"""
        nome = params.get('nome')
        descricao = params.get('descricao', '')
        
        if not nome:
            return "❌ Nome do quadro não especificado. Por favor, informe o nome do quadro que deseja criar."
        
        # Obtém as credenciais diretamente das variáveis de ambiente
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            return "❌ Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
        
        try:
            # Parâmetros para criar quadro
            board_params = {
                "key": api_key,
                "token": token,
                "name": nome,
                "defaultLists": "false"  # Não criar listas padrão automaticamente
            }
            
            if descricao:
                board_params["desc"] = descricao
            
            # Faz a requisição para criar o quadro
            response = requests.post("https://api.trello.com/1/boards/", params=board_params)
            response.raise_for_status()
            
            board_data = response.json()
            board_id = board_data.get('id')
            board_url = board_data.get('url')
            
            # Cria listas padrão
            listas_padrao = ["A Fazer", "Em Andamento", "Concluído"]
            criadas = []
            
            for lista_nome in listas_padrao:
                try:
                    lista_params = {
                        "key": api_key,
                        "token": token,
                        "name": lista_nome,
                        "idBoard": board_id
                    }
                    
                    lista_response = requests.post("https://api.trello.com/1/lists", params=lista_params)
                    lista_response.raise_for_status()
                    criadas.append(lista_nome)
                except:
                    pass
            
            resultado = f"✅ Quadro '{nome}' criado com sucesso!\n"
            resultado += f"ID: {board_id}\n"
            resultado += f"URL: {board_url}\n"
            
            if criadas:
                resultado += f"\nListas criadas: {', '.join(criadas)}\n"
            
            resultado += f"\nPara usar este quadro, você pode executar:\n"
            resultado += f"  arcee trello iniciar --board {board_id}"
            
            return resultado
            
        except requests.exceptions.RequestException as e:
            erro = f"❌ Erro ao criar quadro: {str(e)}"
            if hasattr(e, 'response') and e.response:
                erro += f"\nResposta: {e.response.text}"
            return erro
    
    def _comando_apagar_quadro(self, params: Dict[str, Any]) -> str:
        """Processa o comando para apagar um quadro"""
        import requests
        import re
        
        # Verifica se temos URL ou ID
        quadro_url = params.get('quadro_url')
        quadro_id = params.get('quadro_id')
        
        # Se temos URL, extrai o ID
        if quadro_url and not quadro_id:
            match = re.search(r'trello\.com/b/([^/]+)', quadro_url)
            if match:
                quadro_id = match.group(1)
            else:
                return "❌ URL inválida. Formato esperado: https://trello.com/b/BOARD_ID/..."
        
        if not quadro_id:
            return "❌ ID ou URL do quadro não encontrado na mensagem. Tente novamente especificando o ID ou URL completa do quadro."
        
        # Obtém as credenciais diretamente do ambiente
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            return "❌ Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
        
        try:
            # Parâmetros para verificar informações do quadro
            info_params = {
                "key": api_key,
                "token": token
            }
            
            # Verifica se o quadro existe e obtém informações
            info_response = requests.get(f"https://api.trello.com/1/boards/{quadro_id}", params=info_params)
            info_response.raise_for_status()
            
            board_info = info_response.json()
            board_name = board_info.get('name', 'Quadro sem nome')
            
            # Confirma a operação (simples, já que estamos no chat)
            confirmacao = f"⚠️ ATENÇÃO: Você solicitou a exclusão do quadro '{board_name}' (ID: {quadro_id}).\n"
            confirmacao += "Esta operação é irreversível. Para confirmar, digite 'sim' na próxima mensagem."
            
            # Armazena o quadro pendente de exclusão
            self.quadros_pendentes_exclusao[quadro_id] = board_name
            
            return confirmacao
            
        except requests.exceptions.RequestException as e:
            erro = f"❌ Erro ao verificar quadro: {str(e)}"
            if hasattr(e, 'response') and e.response:
                erro += f"\nResposta: {e.response.text}"
            return erro
    
    def _comando_confirmar(self) -> str:
        """Processa o comando para confirmar uma operação"""
        import requests
        
        # Verifica se há algum quadro pendente de exclusão
        if not self.quadros_pendentes_exclusao:
            return "❌ Nenhuma operação pendente de confirmação."
        
        # Obtém as credenciais diretamente do ambiente
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            self.quadros_pendentes_exclusao.clear()
            return "❌ Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
        
        # Processa cada quadro pendente
        resultados = []
        quadros_a_excluir = list(self.quadros_pendentes_exclusao.items())
        
        for quadro_id, quadro_nome in quadros_a_excluir:
            try:
                # Parâmetros da requisição
                params = {
                    "key": api_key,
                    "token": token
                }
                
                # Faz a requisição para apagar o quadro
                response = requests.delete(f"https://api.trello.com/1/boards/{quadro_id}", params=params)
                response.raise_for_status()
                
                resultados.append(f"✅ Quadro '{quadro_nome}' (ID: {quadro_id}) apagado com sucesso!")
                # Remove do dicionário de pendentes
                del self.quadros_pendentes_exclusao[quadro_id]
                
            except requests.exceptions.RequestException as e:
                erro = f"❌ Erro ao apagar quadro '{quadro_nome}' (ID: {quadro_id}): {str(e)}"
                if hasattr(e, 'response') and e.response:
                    erro += f"\nResposta: {e.response.text}"
                resultados.append(erro)
        
        # Limpa quaisquer quadros restantes
        self.quadros_pendentes_exclusao.clear()
        
        # Retorna os resultados
        if not resultados:
            return "❌ Nenhum quadro foi processado."
        elif len(resultados) == 1:
            return resultados[0]
        else:
            return "\n".join(resultados)
    
    def _comando_buscar_card(self, params: Dict[str, Any]) -> str:
        """Processa o comando para buscar um card pelo nome."""
        import requests
        import os
        
        # Verifica se temos o nome do card a ser buscado
        if 'card_nome' not in params:
            return "Por favor, especifique o nome ou parte do nome do card a ser buscado."
        
        termo_busca = params['card_nome']
        
        # Obtém as credenciais do Trello
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            return "Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
        
        # Parâmetros base para as requisições
        auth_params = {
            "key": api_key,
            "token": token
        }
        
        # Quadros a serem pesquisados
        quadros_para_buscar = []
        
        try:
            # Se foi fornecido um ID de quadro específico
            if 'quadro_id' in params:
                # Verifica se o quadro existe
                response = requests.get(f"https://api.trello.com/1/boards/{params['quadro_id']}", params=auth_params)
                response.raise_for_status()
                board_info = response.json()
                quadros_para_buscar.append({"id": params['quadro_id'], "name": board_info.get("name", "N/A")})
            
            # Se foi fornecido um nome de quadro
            elif 'quadro_nome' in params:
                # Lista todos os quadros e filtra pelo nome
                response = requests.get("https://api.trello.com/1/members/me/boards", params=auth_params)
                response.raise_for_status()
                all_boards = response.json()
                
                # Filtra os quadros pelo nome (case insensitive)
                matching_boards = [
                    board for board in all_boards 
                    if params['quadro_nome'].lower() in board.get("name", "").lower()
                ]
                
                if not matching_boards:
                    return f"Nenhum quadro encontrado com o nome '{params['quadro_nome']}'."
                
                for board in matching_boards:
                    quadros_para_buscar.append({"id": board.get("id"), "name": board.get("name")})
            
            # Se não foi especificado nenhum quadro, busca em todos
            else:
                response = requests.get("https://api.trello.com/1/members/me/boards", params=auth_params)
                response.raise_for_status()
                all_boards = response.json()
                
                if not all_boards:
                    return "Nenhum quadro encontrado na sua conta do Trello."
                
                for board in all_boards:
                    quadros_para_buscar.append({"id": board.get("id"), "name": board.get("name")})
            
            # Para armazenar os resultados encontrados
            resultados = []
            
            # Para cada quadro, busca os cards e as listas
            for quadro in quadros_para_buscar:
                board_id = quadro["id"]
                board_name = quadro["name"]
                
                # Obtém todas as listas do quadro para mapear IDs para nomes
                lists_response = requests.get(f"https://api.trello.com/1/boards/{board_id}/lists", params=auth_params)
                lists_response.raise_for_status()
                board_lists = lists_response.json()
                lists_dict = {lst.get("id"): lst.get("name") for lst in board_lists}
                
                # Obtém todos os cards do quadro
                cards_response = requests.get(f"https://api.trello.com/1/boards/{board_id}/cards", params=auth_params)
                cards_response.raise_for_status()
                board_cards = cards_response.json()
                
                # Filtra os cards pelo termo de busca
                matching_cards = [
                    card for card in board_cards 
                    if termo_busca.lower() in card.get("name", "").lower()
                ]
                
                # Adiciona os resultados encontrados
                for card in matching_cards:
                    resultados.append({
                        "card_id": card.get("id"),
                        "card_name": card.get("name"),
                        "card_url": card.get("shortUrl") or card.get("url"),
                        "board_id": board_id,
                        "board_name": board_name,
                        "list_id": card.get("idList"),
                        "list_name": lists_dict.get(card.get("idList"), "Lista desconhecida")
                    })
            
            # Exibe os resultados
            if not resultados:
                return f"Nenhum card encontrado com o termo '{termo_busca}'."
            
            # Formata a resposta
            if len(resultados) == 1:
                r = resultados[0]
                return f"Card encontrado: {r['card_name']}\nQuadro: {r['board_name']}\nLista: {r['list_name']}\nURL: {r['card_url']}"
            
            resposta = f"Encontrados {len(resultados)} cards correspondentes:\n\n"
            
            for i, r in enumerate(resultados, 1):
                resposta += f"{i}. Card: {r['card_name']}\n"
                resposta += f"   Quadro: {r['board_name']}\n"
                resposta += f"   Lista: {r['list_name']}\n"
                resposta += f"   URL: {r['card_url']}\n\n"
            
            return resposta.strip()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro ao acessar a API do Trello: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f"\nResposta: {e.response.text}"
            logger.exception(error_msg)
            return error_msg
        
        except Exception as e:
            error_msg = f"Erro inesperado durante a busca: {str(e)}"
            logger.exception(error_msg)
            return error_msg
    
    # Métodos para gerenciar o cache
    def _cache_valido(self, cache_key: str, board_id: Optional[str] = None, list_id: Optional[str] = None) -> bool:
        """
        Verifica se o cache para um determinado recurso ainda é válido
        
        Args:
            cache_key: Chave do cache (boards, lists, cards)
            board_id: ID do quadro (para listas)
            list_id: ID da lista (para cards)
            
        Returns:
            bool: True se o cache é válido, False caso contrário
        """
        import time
        
        now = time.time()
        
        if cache_key == 'boards':
            return (self.cache[cache_key]['data'] is not None and 
                    now - self.cache[cache_key]['timestamp'] < self.cache_ttl)
        
        elif cache_key == 'lists' and board_id:
            return (board_id in self.cache[cache_key] and 
                    self.cache[cache_key][board_id]['data'] is not None and 
                    now - self.cache[cache_key][board_id]['timestamp'] < self.cache_ttl)
        
        elif cache_key == 'cards' and list_id:
            return (list_id in self.cache[cache_key] and 
                    self.cache[cache_key][list_id]['data'] is not None and 
                    now - self.cache[cache_key][list_id]['timestamp'] < self.cache_ttl)
        
        return False
    
    def _get_from_cache(self, cache_key: str, board_id: Optional[str] = None, list_id: Optional[str] = None) -> Any:
        """
        Obtém dados do cache
        
        Args:
            cache_key: Chave do cache (boards, lists, cards)
            board_id: ID do quadro (para listas)
            list_id: ID da lista (para cards)
            
        Returns:
            Dados armazenados no cache ou None se não disponível
        """
        if not self._cache_valido(cache_key, board_id, list_id):
            return None
        
        if cache_key == 'boards':
            return self.cache[cache_key]['data']
        
        elif cache_key == 'lists' and board_id:
            return self.cache[cache_key][board_id]['data']
        
        elif cache_key == 'cards' and list_id:
            return self.cache[cache_key][list_id]['data']
        
        return None
    
    def _store_in_cache(self, cache_key: str, data: Any, board_id: Optional[str] = None, list_id: Optional[str] = None) -> None:
        """
        Armazena dados no cache
        
        Args:
            cache_key: Chave do cache (boards, lists, cards)
            data: Dados a serem armazenados
            board_id: ID do quadro (para listas)
            list_id: ID da lista (para cards)
        """
        import time
        
        now = time.time()
        
        if cache_key == 'boards':
            self.cache[cache_key] = {'data': data, 'timestamp': now}
        
        elif cache_key == 'lists' and board_id:
            if board_id not in self.cache[cache_key]:
                self.cache[cache_key][board_id] = {}
            self.cache[cache_key][board_id] = {'data': data, 'timestamp': now}
        
        elif cache_key == 'cards' and list_id:
            if list_id not in self.cache[cache_key]:
                self.cache[cache_key][list_id] = {}
            self.cache[cache_key][list_id] = {'data': data, 'timestamp': now} 