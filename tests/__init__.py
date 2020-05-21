# -*- coding: utf-8 -*-
"""An extremely simple command-line application."""

# third-party imports
import click
from loguru import logger

# module imports
from click_loguru import ClickLoguru

# global constants
LOG_FILE_RETENTION = 3
VERSION = "0.2.0"
NAME = "simple"

# define the CLI
click_loguru = ClickLoguru(
    NAME, VERSION, retention=LOG_FILE_RETENTION, log_dir_parent="tests/data/"
)


@click_loguru.logging_options
@click.group()
@click_loguru.stash_subcommand()
@click.version_option(version=VERSION, prog_name=NAME)
def cli(verbose, quiet, logfile):
    """simple -- a simple cli function with logging by loguru."""
    unused_str = f"verbose: {verbose} quiet: {quiet} logfile: {logfile}"


@cli.command()
@click_loguru.init_logger()
@click_loguru.log_elapsed_time()
def test_logging():
    """Log at different severity levels."""
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")


@cli.command()
@click_loguru.init_logger(logfile=False)
def show_context():
    "Print value of global quiet option."
    options = click_loguru.get_global_options()
    print(f"{options}")


@cli.command()
@click_loguru.init_logger(logfile=False)
def quiet_value():
    "Print value of global quiet option."
    options = click_loguru.get_global_options()
    print(f"{options.quiet:d}", end="")
