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
            # Tenta extrair o nome da lista
            match_lista = re.search(r'(?:na|no|da|do)\s+lista\s+(?:chamada\s+|com\s+nome\s+)?["\']?([^"\']+)["\']?', texto)
            if match_lista:
                params['lista_nome'] = match_lista.group(1).strip()
                
            # Tenta extrair o nome do card
            match_nome = re.search(r'(?:chamado|com\s+nome|nome|título)\s+["\']?([^"\']+)["\']?', texto)
            if match_nome:
                params['nome'] = match_nome.group(1).strip()
                
            # Tenta extrair a descrição
            match_desc = re.search(r'(?:descrição|com\s+descrição)\s+["\']?([^"\']+)["\']?', texto)
            if match_desc:
                params['descricao'] = match_desc.group(1).strip()
        
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
        """Processa o comando para listar todos os quadros do usuário"""
        import requests
        
        # Obtém as credenciais diretamente do ambiente
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            return "❌ Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
        
        try:
            # Parâmetros da requisição
            params = {
                "key": api_key,
                "token": token,
                "filter": "open" # Apenas quadros abertos
            }
            
            # Faz a requisição para obter os quadros
            # Busca os quadros que o usuário tem acesso
            response = requests.get("https://api.trello.com/1/members/me/boards", params=params)
            response.raise_for_status()
            
            quadros = response.json()
            
            if not quadros:
                return "ℹ️ Nenhum quadro encontrado."
                
            # Formata os quadros em texto
            result = "📋 Quadros do Trello:\n\n"
            
            for quadro in quadros:
                nome = quadro.get('name', 'N/A')
                id_quadro = quadro.get('id', 'N/A')
                url = quadro.get('shortUrl', 'N/A')
                desc = quadro.get('desc', '')
                
                result += f"• {nome}\n"
                result += f"  ID: {id_quadro}\n"
                result += f"  URL: {url}\n"
                if desc:
                    result += f"  Descrição: {desc}\n"
                result += "\n"
                
            return result
            
        except requests.exceptions.RequestException as e:
            erro = f"❌ Erro ao listar quadros: {str(e)}"
            if hasattr(e, 'response') and e.response:
                erro += f"\nResposta: {e.response.text}"
            return erro
    
    def _comando_listar_listas(self, params: Optional[Dict[str, Any]] = None) -> str:
        """Processa o comando para listar listas"""
        import requests
        
        if params is None:
            params = {}
        
        # Obtém as credenciais diretamente do ambiente
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            return "❌ Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
        
        # Verifica se foi especificado um ID de quadro no comando
        board_id = params.get('quadro_id')
        
        # Se não foi especificado, usa o valor padrão do .env
        if not board_id:
            board_id = os.getenv("TRELLO_BOARD_ID")
            if not board_id:
                return "❌ ID do quadro não encontrado. Especifique o ID do quadro no comando ou defina TRELLO_BOARD_ID no arquivo .env."
            
            quadro_de_referencia = "quadro padrão"
        else:
            quadro_de_referencia = f"quadro com ID {board_id}"
        
        try:
            # Parâmetros da requisição
            request_params = {
                "key": api_key,
                "token": token
            }
            
            # Faz a requisição para obter as listas
            response = requests.get(f"https://api.trello.com/1/boards/{board_id}/lists", params=request_params)
            response.raise_for_status()
            
            listas = response.json()
            
            if not listas:
                return f"ℹ️ Nenhuma lista encontrada no {quadro_de_referencia}."
                
            # Formata as listas em texto
            result = f"📋 Listas do {quadro_de_referencia}:\n\n"
            
            for lista in listas:
                # Para cada lista, obtém o número de cards
                cards_response = requests.get(f"https://api.trello.com/1/lists/{lista['id']}/cards", params=request_params)
                cards_response.raise_for_status()
                cards = cards_response.json()
                
                result += f"• {lista.get('name', 'N/A')} (ID: {lista.get('id', 'N/A')}) - {len(cards)} cards\n"
                
            return result
            
        except requests.exceptions.RequestException as e:
            erro = f"❌ Erro ao listar listas: {str(e)}"
            if hasattr(e, 'response') and e.response:
                erro += f"\nResposta: {e.response.text}"
            return erro
    
    def _comando_listar_cards(self, params: Dict[str, Any]) -> str:
        """Processa o comando para listar cards"""
        if not self.agent:
            return "❌ Agente não disponível para processar comandos do Trello"
            
        lista_nome = params.get('lista_nome')
        lista_id = None
        
        # Se temos um nome de lista, precisamos obter o ID
        if lista_nome:
            listas_response = self.agent.run_tool("get_lists", {"random_string": "dummy"})
            
            if "error" in listas_response:
                return f"❌ Erro: {listas_response['error']}"
                
            # Procura a lista pelo nome
            for lista in listas_response.get("lists", []):
                if lista_nome.lower() in lista.get('name', '').lower():
                    lista_id = lista.get('id')
                    lista_nome_completo = lista.get('name')
                    break
            
            if not lista_id:
                return f"❌ Lista '{lista_nome}' não encontrada. Verifique o nome e tente novamente."
        
        # Se temos um ID de lista, obtém os cards dessa lista
        if lista_id:
            response = self.agent.run_tool("get_cards_by_list_id", {"listId": lista_id})
            
            if "error" in response:
                return f"❌ Erro: {response['error']}"
                
            # Formata os cards em texto
            result = f"🗂️ Cards da Lista '{lista_nome_completo}':\n\n"
            
            for card in response.get("cards", []):
                result += f"• {card.get('name', 'N/A')} (ID: {card.get('id', 'N/A')})\n"
                if card.get('desc'):
                    result += f"  Descrição: {card.get('desc')[:50]}" + ("..." if len(card.get('desc', '')) > 50 else "") + "\n"
                result += "\n"
                
            return result
        
        # Se não temos ID de lista, obtém todas as listas e seus cards
        else:
            listas_response = self.agent.run_tool("get_lists", {"random_string": "dummy"})
            
            if "error" in listas_response:
                return f"❌ Erro: {listas_response['error']}"
                
            # Formata os cards em texto, agrupados por lista
            result = "🗂️ Todos os Cards do Trello:\n\n"
            
            for lista in listas_response.get("lists", []):
                lista_id = lista.get("id")
                lista_nome = lista.get("name")
                
                # Adiciona cabeçalho da lista
                result += f"📋 Lista: {lista_nome}\n"
                
                # Obtém os cards da lista
                cards_response = self.agent.run_tool("get_cards_by_list_id", {"listId": lista_id})
                
                if "error" not in cards_response:
                    cards = cards_response.get("cards", [])
                    if cards:
                        for card in cards:
                            result += f"• {card.get('name', 'N/A')} (ID: {card.get('id', 'N/A')})\n"
                            if card.get('desc'):
                                result += f"  Descrição: {card.get('desc')[:50]}" + ("..." if len(card.get('desc', '')) > 50 else "") + "\n"
                    else:
                        result += "  (Nenhum card)\n"
                else:
                    result += f"  ❌ Erro ao obter cards: {cards_response.get('error')}\n"
                
                result += "\n"
                
            return result
    
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
        
        nome = params.get('nome')
        descricao = params.get('descricao', '')
        lista_nome = params.get('lista_nome')
        lista_id = params.get('lista_id')
        
        if not nome:
            return "❌ Nome do card não especificado. Por favor, informe o nome do card que deseja criar."
            
        # Obtém as credenciais diretamente do ambiente
        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        
        if not api_key or not token:
            return "❌ Credenciais do Trello não encontradas. Verifique se TRELLO_API_KEY e TRELLO_TOKEN estão definidos."
        
        try:
            # Se temos o nome da lista mas não o ID, precisamos obter o ID
            if lista_nome and not lista_id:
                # Lista todas as listas do quadro para encontrar o ID da lista especificada
                board_id = os.getenv("TRELLO_BOARD_ID")
                if not board_id:
                    return "❌ ID do quadro não encontrado. Verifique se TRELLO_BOARD_ID está definido no arquivo .env."
                
                listas_params = {
                    "key": api_key,
                    "token": token
                }
                
                # Obtém as listas do quadro
                listas_response = requests.get(f"https://api.trello.com/1/boards/{board_id}/lists", params=listas_params)
                listas_response.raise_for_status()
                
                listas_data = listas_response.json()
                
                # Procura a lista pelo nome
                lista_encontrada = None
                for lista in listas_data:
                    if lista_nome.lower() in lista.get('name', '').lower():
                        lista_encontrada = lista
                        break
                
                if not lista_encontrada:
                    return f"❌ Lista '{lista_nome}' não encontrada. Verifique o nome e tente novamente."
                
                lista_id = lista_encontrada['id']
                lista_nome_completo = lista_encontrada['name']
            
            # Se ainda não temos o ID da lista, não podemos continuar
            if not lista_id:
                return "❌ ID ou nome da lista não especificado. Por favor, informe em qual lista o card deve ser criado."
                
            # Parâmetros para criar o card
            card_params = {
                "key": api_key,
                "token": token,
                "idList": lista_id,
                "name": nome,
                "desc": descricao
            }
            
            # Cria o card
            card_response = requests.post("https://api.trello.com/1/cards", params=card_params)
            card_response.raise_for_status()
            
            card_data = card_response.json()
            
            resultado = f"✅ Card '{nome}' criado com sucesso!\n"
            resultado += f"ID do card: {card_data['id']}\n"
            resultado += f"URL do card: {card_data['url']}\n"
            
            if lista_nome_completo:
                resultado += f"Na lista: {lista_nome_completo}"
            
            return resultado
            
        except requests.exceptions.RequestException as e:
            erro = f"❌ Erro ao criar card: {str(e)}"
            if hasattr(e, 'response') and e.response:
                erro += f"\nResposta: {e.response.text}"
            return erro
    
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