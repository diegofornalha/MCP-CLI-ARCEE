#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar dependências e diagnosticar problemas com a instalação
"""

import importlib
import sys
import subprocess
import os
import pkg_resources

def check_package(package_name):
    """Verifica se um pacote está instalado e sua versão"""
    try:
        package = importlib.import_module(package_name)
        try:
            version = pkg_resources.get_distribution(package_name).version
            return True, version, None
        except pkg_resources.DistributionNotFound:
            return True, "Desconhecida", None
    except ImportError as e:
        return False, None, str(e)

def print_result(name, installed, version, error=None):
    """Exibe o resultado de forma formatada"""
    if installed:
        print(f"✅ {name}: INSTALADO (versão {version})")
    else:
        print(f"❌ {name}: NÃO INSTALADO")
        if error:
            print(f"   Erro: {error}")

def check_imports(package_name, import_items=None):
    """Tenta importar módulos específicos de um pacote"""
    if not import_items:
        return
    
    print(f"\nVerificando importações de {package_name}:")
    
    for item in import_items:
        try:
            import_cmd = f"from {package_name} import {item}"
            exec(import_cmd)
            print(f"  ✅ {import_cmd}")
        except ImportError as e:
            print(f"  ❌ {import_cmd}")
            print(f"     Erro: {e}")
        except Exception as e:
            print(f"  ⚠️ {import_cmd}")
            print(f"     Erro inesperado: {e}")

def check_python_path():
    """Verifica o Python Path"""
    print("\nPYTHON PATH:")
    for path in sys.path:
        print(f"  - {path}")

def main():
    """Função principal"""
    print("==== VERIFICADOR DE DEPENDÊNCIAS ====\n")
    
    packages = [
        ("mcp-run", ["Client"]),
        ("crewai", ["Agent", "Crew", "Process", "Task"]),
        ("pyyaml", ["safe_load", "safe_dump"]),
        ("openai", ["OpenAI"]),
        ("typer", []),
        ("rich", ["print", "Panel"]),
    ]
    
    for package, import_items in packages:
        installed, version, error = check_package(package.replace("-", "_"))
        print_result(package, installed, version, error)
        
        if installed and import_items:
            check_imports(package.replace("-", "_"), import_items)
    
    check_python_path()
    
    print("\n==== FIM DA VERIFICAÇÃO ====")

if __name__ == "__main__":
    main() 