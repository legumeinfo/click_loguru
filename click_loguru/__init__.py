# -*- coding: utf-8 -*-
"""click_loguru -- Setup loguru logging with stderr and file with click."""

# standard library imports
import functools
import sys
from datetime import datetime
from pathlib import Path

# third-party imports
import attr
from click import option
from click import get_current_context as cur_ctx
from loguru import logger

# global constants
__version__ = "1.0.0"
__all__ = ["ClickLoguru"]
STARTTIME = datetime.now()
DEFAULT_STDERR_LOG_LEVEL = "INFO"
DEFAULT_FILE_LOG_LEVEL = "DEBUG"
NO_LEVEL_BELOW = 30  # Don't print level for messages below this level


class ClickLoguru:
    """Creates decorators for use with click to control loguru logging ."""

    @attr.s
    class LogState(object):
        """Click context object for verbosity, quiet, and logfile info."""

        verbose = False
        quiet = False
        logfile = True
        logfile_path = ""
        logfile_handler_id = None
        subcommand = None

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
        self._name = name
        self._version = version
        self._retention = retention
        self._log_dir_parent = log_dir_parent
        self._file_log_level = file_log_level
        self._stderr_log_level = stderr_log_level
        if stderr_format_func is None:

            def format_func(msgdict):
                """Do level-sensitive formatting."""
                if msgdict["level"].no < NO_LEVEL_BELOW:
                    return "<level>{message}</level>\n"
                return "<level>{level}</level>: <level>{message}</level>\n"

            self.stderr_format_func = format_func
        else:
            self.stderr_format_func = stderr_format_func

    def _verbose_option(self, user_func):
        """Define verbose option."""

        def callback(ctx, unused_param, value):
            """Set verbose state."""
            state = ctx.ensure_object(self.LogState)
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
        )(user_func)

    def _quiet_option(self, user_func):
        """Define quiet option."""

        def callback(ctx, unused_param, value):
            """Set quiet state."""
            state = ctx.ensure_object(self.LogState)
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
        )(user_func)

    def _logfile_option(self, user_func):
        """Define logfile option."""

        def callback(ctx, unused_param, value):
            """Set logfile state."""
            state = ctx.ensure_object(self.LogState)
            state.logfile = value
            return value

        return option(
            "--logfile/--no-logfile",
            is_flag=True,
            show_default=True,
            default=True,
            help="Log to file.",
            callback=callback,
        )(user_func)

    def logging_options(self, user_func):
        """Set all logging options."""
        user_func = self._verbose_option(user_func)
        user_func = self._quiet_option(user_func)
        user_func = self._logfile_option(user_func)
        return user_func

    def init_logger(self, log_dir_parent=None, logfile=True):
        """Log to stderr and to logfile at different levels."""

        def decorator(user_func):
            @functools.wraps(user_func)
            def wrapper(*args, **kwargs):
                state = cur_ctx().find_object(self.LogState)
                # get the verbose/quiet levels from context
                if state.verbose:
                    log_level = "DEBUG"
                elif state.quiet:
                    log_level = "ERROR"
                else:
                    log_level = self._stderr_log_level
                logger.remove()  # remove existing default logger
                logger.add(
                    sys.stderr, level=log_level, format=self.stderr_format_func
                )
                if logfile and state.logfile:  # start a log file
                    # If a subcommand was used, log to a file in the
                    # logs/ subdirectory with the subcommand in the file name.
                    if log_dir_parent is not None:
                        self._log_dir_parent = log_dir_parent
                    if self._log_dir_parent is None:
                        log_dir_path = Path(".") / "logs"
                    else:
                        log_dir_path = Path(self._log_dir_parent)
                    subcommand = cur_ctx().invoked_subcommand
                    if subcommand is None:
                        subcommand = state.subcommand
                    if subcommand is not None:
                        logfile_prefix = f"{self._name}-{subcommand}"
                    else:
                        logfile_prefix = f"{self._name}"
                    if log_dir_path.exists():
                        log_numbers = [
                            f.name[len(logfile_prefix) + 1 : -4]
                            for f in log_dir_path.glob(
                                logfile_prefix + "_*.log"
                            )
                        ]
                        log_number_ints = sorted(
                            [int(n) for n in log_numbers if n.isnumeric()]
                        )
                        if len(log_number_ints) > 0:
                            log_number = log_number_ints[-1] + 1
                            if (
                                self._retention is not None
                                and len(log_number_ints) > self._retention
                            ):
                                for remove in log_number_ints[
                                    : len(log_number_ints) - self._retention
                                ]:
                                    (
                                        log_dir_path
                                        / f"{logfile_prefix}_{remove}.log"
                                    ).unlink()
                        else:
                            log_number = 0
                    else:
                        log_number = 0
                    if self._retention == 0:
                        state.logfile_path = (
                            log_dir_path / f"{logfile_prefix}.log"
                        )
                    else:
                        state.logfile_path = (
                            log_dir_path / f"{logfile_prefix}_{log_number}.log"
                        )
                    state.logfile_handler_id = logger.add(
                        str(state.logfile_path), level=self._file_log_level
                    )
                logger.debug(f'Command line: "{" ".join(sys.argv)}"')
                logger.debug(f"{self._name} version {self._version}")
                logger.debug(f"Run started at {str(STARTTIME)[:-7]}")
                return user_func(*args, **kwargs)

            return wrapper

        return decorator

    def log_elapsed_time(self):
        """Log the elapsed time for (sub)command."""

        def decorator(user_func):
            @functools.wraps(user_func)
            def wrapper(*args, **kwargs):
                returnobj = user_func(*args, **kwargs)
                logger.debug(
                    f"Elapsed time is {str(datetime.now() - STARTTIME)[:-7]}"
                )
                return returnobj

            return wrapper

        return decorator

    def stash_subcommand(self):
        """Save the subcommand to the context object."""

        def decorator(user_func):
            @functools.wraps(user_func)
            def wrapper(*args, **kwargs):
                state = cur_ctx().find_object(self.LogState)
                state.subcommand = cur_ctx().invoked_subcommand
                return user_func(*args, **kwargs)

            return wrapper

        return decorator

    def get_global_options(self):
        """Return dictionary of global options."""
        return cur_ctx().find_object(self.LogState)
