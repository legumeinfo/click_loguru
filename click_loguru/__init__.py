# -*- coding: utf-8 -*-
"""click_loguru -- Setup loguru logging with stderr and file with click."""

# standard library imports
import functools
import sys
from datetime import datetime
from pathlib import Path

# third-party imports
from click import option
from click import get_current_context as ctx
from loguru import logger

# global constants
__version__ = "0.1.0"
STARTTIME = datetime.now()
DEFAULT_STDERR_LOG_LEVEL = "INFO"
DEFAULT_FILE_LOG_LEVEL = "DEBUG"
NO_LEVEL_BELOW = 30  # Don't print level for messages below this level


class LogState(object):
    """Click context object for verbosity, quiet, and logfile info."""

    def __init__(self):
        "Initialize logging object with default values."
        self.verbose = False
        self.quiet = False
        self.logfile = True
        self.logfile_handler_id = None
        self.subcommand = None

    def __repr__(self):
        """Print logging state variables."""
        retstr = f"verbose: {self.verbose}\n"
        retstr += f"quiet: {self.quiet}\n"
        retstr += f"logfile: {self.logfile}\n"
        if self.subcommand is None:
            retstr += "No subcommand.\n"
        else:
            retstr += f"Subcommand is {self.subcommand}.\n"
        if self.logfile_handler_id is None:
            retstr += "No logfile handler."
        else:
            retstr += "logfile handler is present."
        return retstr


class ClickLoguru(object):

    """Creates decorators for use with click to control loguru logging ."""

    def __init__(
        self,
        name,
        version,
        retention=None,
        stderr_format_func=None,
        log_dir_parent=None,
        file_log_level=DEFAULT_FILE_LOG_LEVEL,
        stderr_log_level=DEFAULT_STDERR_LOG_LEVEL,
    ):
        """Initialize logging setup info."""
        self.name = name
        self.version = version
        self.retention = retention
        self.log_dir_parent = log_dir_parent
        self.file_log_level = file_log_level
        self.stderr_log_level = stderr_log_level
        if stderr_format_func == None:

            def format_func(msgdict):
                """This function is used for level-sensitive formatting."""
                if msgdict["level"].no < NO_LEVEL_BELOW:
                    return "<level>{message}</level>\n"
                else:
                    return "<level>{level}</level>: <level>{message}</level>\n"

            self.stderr_format_func = format_func
        else:
            self.stderr_format_func = stderr_format_func

    def _verbose_option(self, f):
        """Define verbose option."""

        def callback(ctx, param, value):
            """Set verbose state."""
            state = ctx.ensure_object(LogState)
            state.verbose = value
            return value

        return option(
            "-v",
            "--verbose",
            is_flag=True,
            show_default=True,
            default=False,
            help="Log debugging info to stderr.",
            callback=callback,
        )(f)

    def _quiet_option(self, f):
        """Define quiet option."""

        def callback(ctx, param, value):
            """Set quiet state."""
            state = ctx.ensure_object(LogState)
            state.quiet = value
            return value

        return option(
            "-q",
            "--quiet",
            is_flag=True,
            show_default=True,
            default=False,
            help="Suppress info to stderr.",
            callback=callback,
        )(f)

    def _logfile_option(self, f):
        """Define logfile option."""

        def callback(ctx, param, value):
            """Set logfile state."""
            state = ctx.ensure_object(LogState)
            state.logfile = value
            return value

        return option(
            "--logfile/--no-logfile",
            is_flag=True,
            show_default=True,
            default=True,
            help=f"Log to file.",
            callback=callback,
        )(f)

    def logging_options(self, f):
        """Set all logging options."""
        f = self._verbose_option(f)
        f = self._quiet_option(f)
        f = self._logfile_option(f)
        return f

    def init_logger(self, log_dir_parent=None, logfile=True):
        """Log to stderr and to logfile at different levels."""

        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                state = ctx().find_object(LogState)
                # get the verbose/quiet levels from context
                if state.verbose:
                    log_level = "DEBUG"
                elif state.quiet:
                    log_level = "ERROR"
                else:
                    log_level = self.stderr_log_level
                logger.remove()  # remove existing default logger
                logger.add(sys.stderr, level=log_level, format=self.stderr_format_func)
                if logfile and state.logfile:  # start a log file
                    # If a subcommand was used, log to a file in the
                    # logs/ subdirectory with the subcommand in the file name.
                    if log_dir_parent is not None:
                        self.log_dir_parent = log_dir_parent
                    if self.log_dir_parent == None:
                        log_dir_parent_path = Path(".")
                    else:
                        log_dir_parent_path = Path(self.log_dir_parent)
                    log_dir_path = log_dir_parent_path / "logs"
                    subcommand = ctx().invoked_subcommand
                    if subcommand is None:
                        subcommand = state.subcommand
                    if subcommand is not None:
                        logfile_prefix = f"{self.name}-{subcommand}"
                    else:
                        logfile_prefix = f"{self.name}"
                    if log_dir_path.exists():
                        log_numbers = [
                            f.name[len(logfile_prefix) + 1 : -4] for f in log_dir_path.glob(logfile_prefix + "_*.log")
                        ]
                        log_number_ints = sorted([int(n) for n in log_numbers if n.isnumeric()])
                        if len(log_number_ints):
                            log_number = log_number_ints[-1] + 1
                            if self.retention is not None and len(log_number_ints) > self.retention:
                                for remove in log_number_ints[: len(log_number_ints) - self.retention]:
                                    (log_dir_path / f"{logfile_prefix}_{remove}.log").unlink()
                        else:
                            log_number = 0
                    else:
                        log_number = 0
                    logfile_path = log_dir_path / f"{logfile_prefix}_{log_number}.log"
                    state.logfile_handler_id = logger.add(str(logfile_path), level=self.file_log_level)
                logger.debug(f'Command line: "{" ".join(sys.argv)}"')
                logger.debug(f"{self.name} version {self.version}")
                logger.debug(f"Run started at {str(STARTTIME)[:-7]}")
                return f(*args, **kwargs)

            return wrapper

        return decorator

    def log_elapsed_time(self):
        """Log the elapsed time for command."""

        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                returnobj = f(*args, **kwargs)
                logger.debug(f"Elapsed time is {str(datetime.now() - STARTTIME)[:-7]}")
                return returnobj

            return wrapper

        return decorator

    def stash_subcommand(self):
        """Save the subcommand to the context object"""

        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                state = ctx().find_object(LogState)
                state.subcommand = ctx().invoked_subcommand
                return f(*args, **kwargs)

            return wrapper

        return decorator

    def test_log_func(self, cli):
        """Define the test_logging command."""

        @cli.command()
        @self.init_logger()
        @self.log_elapsed_time()
        def test_logging():
            """Log at different severity levels."""
            logger.debug("debug message")
            logger.info("info message")
            logger.warning("warning message")
            logger.error("error message")

        return test_logging

    def show_context_func(self, cli):
        """Define the show_context_dict command."""

        @cli.command()
        @self.init_logger(logfile=False)
        def show_loguru_context():
            """Print the global context dictionary."""
            print(ctx().find_object(LogState))

        return show_loguru_context
