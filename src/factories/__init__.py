#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pacote de fábricas (factories)

Este pacote fornece fábricas para criar instâncias de serviços e clientes
abstraindo a implementação concreta e simplificando a injeção de dependências.
"""

from src.factories.service_factory import ServiceFactory

__all__ = ['ServiceFactory'] 