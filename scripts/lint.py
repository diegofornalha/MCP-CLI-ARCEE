#!/usr/bin/env python3

import subprocess
import sys


def main():
    """Execute ruff lint and pyright checks."""
    try:
        # Roda o ruff lint
        ruff_result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)

        # Roda o pyright
        pyright_result = subprocess.run(["pyright"], capture_output=True, text=True)

        if ruff_result.returncode != 0:
            print("❌ Erro no Ruff lint:")
            print(ruff_result.stdout)
            print(ruff_result.stderr)
            sys.exit(1)

        if pyright_result.returncode != 0:
            print("❌ Erro no Pyright:")
            print(pyright_result.stdout)
            print(pyright_result.stderr)
            sys.exit(1)

        print("✅ Lint OK!")

    except Exception as e:
        print(f"❌ Erro ao executar lint: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
