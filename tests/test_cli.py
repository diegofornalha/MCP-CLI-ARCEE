"""
Testes para o CLI do Arcee
"""

import pytest
from arcee_cli.arcee_cli import main

def test_cli_help(capsys):
    """Testa se a ajuda do CLI é exibida corretamente"""
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Arcee CLI" in captured.out
    assert "teste" in captured.out
    assert "chat" in captured.out

def test_cli_version(capsys):
    """Testa se a versão do CLI é exibida corretamente"""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Arcee CLI v1.0.0" in captured.out 