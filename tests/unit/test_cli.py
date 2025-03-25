"""
Testes unitários para a CLI do Arcee
"""

from typer.testing import CliRunner
from arcee_cli.__main__ import app

runner = CliRunner()


def test_cli_help():
    """Testa se o comando de ajuda funciona"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "CLI do Arcee AI" in result.stdout


def test_cli_configure_help():
    """Testa se o comando de configuração mostra ajuda"""
    result = runner.invoke(app, ["configure", "--help"])
    assert result.exit_code == 0
    assert "Configura a CLI do Arcee" in result.stdout
