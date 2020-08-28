# -*- coding: utf-8 -*-
"""An extremely simple command-line application."""

# third-party imports
import click
from loguru import logger

# module imports
from click_loguru import ClickLoguru

# global constants
LOG_FILE_RETENTION = 3
VERSION = "0.4.0"
NAME = "simple"

# define the CLI
click_loguru = ClickLoguru(
    NAME,
    VERSION,
    retention=LOG_FILE_RETENTION,
    log_dir_parent="tests/data/logs",
)


@click_loguru.logging_options
@click.group()
@click_loguru.stash_subcommand()
@click.option(
    "-e",
    "--extra",
    is_flag=True,
    show_default=True,
    default=False,
    help="An extra global option.",
    callback=click_loguru.user_global_options_callback,
)
@click.version_option(version=VERSION, prog_name=NAME)
def cli(verbose, quiet, logfile, extra):
    """simple -- a simple cli function with logging by loguru."""
    unused_str = (
        f"verbose: {verbose} quiet: {quiet} logfile: {logfile} extra{extra}"
    )


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
@click_loguru.init_logger()
def show_context():
    "Print value of global quiet option."
    state = click_loguru.get_global_options()
    print(f"verbose: {state.verbose}")
    print(f"quiet: {state.quiet}")
    print(f"logfile: {state.logfile}")
    if state.subcommand is None:
        print("No subcommand")
    else:
        print(f'Subcommand: "{state.subcommand}"')
    if state.logfile_handler_id is None:
        print("No logfile handler.")
    else:
        print(f'Logfile path: "{state.logfile_path}"')
    print(f"{state}")


@cli.command()
@click_loguru.init_logger(logfile=False)
def quiet_value():
    "Print value of global quiet option."
    state = click_loguru.get_global_options()
    print(f"{state.quiet:d}", end="")


@cli.command()
@click_loguru.init_logger(logfile=False)
def extra_value():
    "Print value of global quiet option."
    user_options = click_loguru.get_user_global_options()
    print(f"{user_options['extra']:d}", end="")
