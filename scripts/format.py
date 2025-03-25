#!/usr/bin/env python3

import subprocess
import sys


def main():
    """Execute ruff format check."""
    try:
        # Roda o ruff format em modo check
        result = subprocess.run(["ruff", "format", "--check", "."], capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Erro na formatação:")
            print(result.stdout)
            print(result.stderr)
            sys.exit(1)

        print("✅ Formatação OK!")

    except Exception as e:
        print(f"❌ Erro ao executar ruff format: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
