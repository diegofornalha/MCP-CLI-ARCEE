#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comando para configurar a CLI do Arcee AI
"""

import json
import os
from typing import Optional

from rich import print
from rich.prompt import Prompt


def configure(
    api_key: Optional[str] = None,
    org: Optional[str] = None,
):
    """Configura a CLI do Arcee"""
    config_dir = os.path.expanduser("~/.arcee")
    config_file = os.path.join(config_dir, "config.json")

    # Criar diretório se não existir
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Carregar configuração existente
    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {str(e)}")

    # Solicitar valores não fornecidos
    if not api_key:
        api_key = Prompt.ask(
            "🔑 Digite sua chave de API",
            default=config.get("api_key", ""),
            password=True,
        )

    if not org:
        org = Prompt.ask(
            "🏢 Digite sua organização (opcional)",
            default=config.get("org", ""),
        )

    # Atualizar configuração
    config.update(
        {
            "api_key": api_key,
            "org": org,
        }
    )

    # Salvar configuração
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print("\n✅ Configuração salva com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao salvar configuração: {str(e)}")
