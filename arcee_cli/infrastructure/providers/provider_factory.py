#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fábrica para criar provedores de IA
"""

from typing import Optional
from arcee_cli.infrastructure.providers.arcee_provider import ArceeProvider

# Provedor global para ser reutilizado em diferentes comandos
_provider = None


def get_provider() -> Optional[ArceeProvider]:
    """Obtém um provedor global ou cria um novo se não existir"""
    global _provider
    if _provider is None:
        try:
            _provider = ArceeProvider()
        except Exception as e:
            print(f"❌ Erro ao inicializar provedor: {str(e)}")
    return _provider
