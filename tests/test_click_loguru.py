# -*- coding: utf-8 -*-
"""Test click_loguru via the simple.py app."""
import os
from pathlib import Path

from click.testing import CliRunner
from tests.simple import cli


def test_help():
    """Test help command."""
    runner = CliRunner()
    result = runner.invoke(cli, [])
    print(result.output)
    assert result.exit_code == 0


def test_logging(tmp_path):
    """Test logging to a data file."""
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(cli, ["test-logging"])
    assert result.exit_code == 0
    assert len(list(Path("tests/data/logs").glob("*"))) == 1


def test_retention(tmp_path):
    """Test keeping copies of the log file."""
    runner = CliRunner()
    os.chdir(tmp_path)
    log_count = 0
    while log_count < 10:
        result = runner.invoke(cli, ["test-logging"])
        assert result.exit_code == 0
        log_count += 1
    assert len(list(Path("tests/data/logs").glob("*"))) == 4
