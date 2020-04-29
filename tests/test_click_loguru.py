# -*- coding: utf-8 -*-
import os
from pathlib import Path

from click_loguru import __version__
from click.testing import CliRunner
from tests.simple import cli


def test_version():
    assert __version__ == "0.1.0"


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    print(result.output)
    assert result.exit_code == 0


def test_logging(tmp_path):
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(cli, ["test-logging"])
    assert result.exit_code == 0
    assert len([p for p in Path("tests/data/logs").glob("*")]) == 1


def test_retention(tmp_path):
    runner = CliRunner()
    os.chdir(tmp_path)
    for i in range(10):
        result = runner.invoke(cli, ["test-logging"])
        assert result.exit_code == 0
    assert len([p for p in Path("tests/data/logs").glob("*")]) == 4
