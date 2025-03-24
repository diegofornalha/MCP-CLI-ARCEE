#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de configuração do Arcee CLI
"""

import json
import os
from typing import Dict, Optional

from rich import print
from rich.prompt import Prompt


def _get_config_file() -> str:
    """Retorna o caminho do arquivo de configuração"""
    config_dir = os.path.expanduser("~/.arcee")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return os.path.join(config_dir, "config.json")


def _load_config() -> Dict:
    """Carrega a configuração do arquivo"""
    config_file = _get_config_file()
    if not os.path.exists(config_file):
        return {}

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {str(e)}")
        return {}


def _save_config(config: Dict) -> None:
    """Salva a configuração no arquivo"""
    config_file = _get_config_file()
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"❌ Erro ao salvar configuração: {str(e)}")


def configure(api_key: Optional[str] = None, org: Optional[str] = None) -> None:
    """Configura a CLI do Arcee"""
    config = _load_config()

    # Se não foi fornecida uma chave API, solicita ao usuário
    if not api_key:
        api_key = Prompt.ask(
            "🔑 Digite sua chave API", password=True, default=config.get("api_key", "")
        )

    # Se não foi fornecida uma organização, solicita ao usuário
    if (
        not org
        and Prompt.ask(
            "👥 Deseja configurar uma organização?", choices=["s", "n"], default="n"
        )
        == "s"
    ):
        org = Prompt.ask("Digite o ID da organização", default=config.get("org", ""))

    # Atualiza a configuração
    config["api_key"] = api_key
    if org:
        config["org"] = org
    elif "org" in config:
        del config["org"]

    # Salva a configuração
    _save_config(config)
    print("\n✅ Configuração salva com sucesso!")
