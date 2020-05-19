# -*- coding: utf-8 -*-
"""An extremely simple command-line application."""

# third-party imports
import click
from loguru import logger

# module imports
from click_loguru import ClickLoguru

# global constants
LOG_FILE_RETENTION = 3
VERSION = "0.0.1"
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
    print(f"verbose: {verbose} quiet: {quiet} logfile: {logfile}")


# test commands from click_loguru itself
test_logging = click_loguru.test_log_func(cli)
show_loguru_context = click_loguru.show_context_func(cli)


@cli.command()
@click_loguru.init_logger(logfile=False)
def simple():
    "The simplest of logging functions."
    logger.info("Here is some info.")
    logger.warning("Here is a warning.")
    logger.error("It's an error!")


if __name__ == "__main__":
    cli(False, False, False)
