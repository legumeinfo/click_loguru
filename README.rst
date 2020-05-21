click_loguru
============
``click_loguru`` initializes `loguru <https://github.com/Delgan/loguru/>`_
for logging to stderr and (optionally) a file for use
with a `click <https://click.palletsprojects.com/>`_ CLI.

If your click application uses subcommands (via ``@click.group()``),
log files will include the subcommand in the name.
Log files are numbered, with a retention policy specified.  Log files can be enabled or disabled
per-subcommand and written to a subdirectory your application specifies.  

Global options control verbose, quiet, and logfile creation.  The values of these global
options are accessible from your application.

Instantiation is from a single class, ``ClickLoguru``, with the arguments of the name and version
of your application.  Optional keyworded arguments are the integer ``retention`` to set the number
of log files retained per-application to values other than the default (4), ``log_dir_parent`` to
set the location of the log file directory other than its default value of ``./logs``,
``file_log_level`` to set the level of logging to the file other than the default of ``DEBUG``,
and ``stderr_log_level`` which by default is set to ``INFO``.

The ``logging_options`` method returns a decorator to be used for the CLI method which defines
the global options that allows control of ``quiet``, ``verbose``, and ``logfile`` booleans.

The ``stash_subcommand`` method returns a decorator to be used for the CLI method for applications
which define subcommands.

The ``init_logger`` method returns a decorator which must be used for each subcommand.   It allows
override of the default ``log_dir_parent`` established at instantiation, as well as turning
off file logging for that command by setting ``logfile`` to ``False``.

The ``log_elapsed_time`` method returns a decorator which causes the elapsed time for the subcommand
to be emitted at the ``DEBUG`` level.

The ``get_global_options`` method returns the context object associated with the global options.
The context object is printable.  The attributes of the context object are the booleans ``verbose``,
``quiet``, and ``logfile``, the string ``subcommand`` showing the subcommand that was invoked,
and ``logfile_handler_id`` if your code wishes to manipulate the handler directly.

See the file ``tests/__init__.py`` for usage examples.

Prerequisites
-------------
Python 3.6 or greater is required.
This package is tested under Linux and MacOS using Python 3.7.


Project Status
--------------
+-------------------+------------+
| Latest Release    | |pypi|     |
+-------------------+------------+
| GitHub            | |repo|     |
+-------------------+------------+
| License           | |license|  |
+-------------------+------------+
| Travis Build      | |travis|   |
+-------------------+------------+
| Coverage          | |coverage| |
+-------------------+------------+
| Code Grade        | |codacy|   |
+-------------------+------------+
| Dependencies      | |depend|   |
+-------------------+------------+
| Pre-commit        | |precommit||
+-------------------+------------+
| Issues            | |issues|   |
+-------------------+------------+

.. |pypi| image:: https://img.shields.io/pypi/v/click_loguru.svg
    :target: https://pypi.python.org/pypi/click_loguru
    :alt: Python package

.. |repo| image:: https://img.shields.io/github/commits-since/legumeinfo/click_loguru/0.1.0.svg
    :target: https://github.com/legumeinfo/click_loguru
    :alt: GitHub repository

.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://github.com/legumeinfo/click_loguru/blob/master/LICENSE.txt
    :alt: License terms

.. |travis| image:: https://img.shields.io/travis/legumeinfo/click_loguru.svg
    :target:  https://travis-ci.org/legumeinfo/click_loguru
    :alt: Travis CI

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/6ee5771afe014cffbb32a2f79cf17fff
    :target: https://www.codacy.com/gh/legumeinfo/click_loguru?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=legumeinfo/click_loguru&amp;utm_campaign=Badge_Grade
    :alt: Codacy.io grade

.. |coverage| image:: https://codecov.io/gh/legumeinfo/click_loguru/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/legumeinfo/click_loguru
    :alt: Codecov.io test coverage

.. |precommit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit
    :alt: pre-commit

.. |issues| image:: https://img.shields.io/github/issues/legumeinfo/click_loguru.svg
    :target:  https://github.com/legumeinfo/click_loguru/issues
    :alt: Issues reported


.. |depend| image:: https://api.dependabot.com/badges/status?host=github&repo=legumeinfo/click_loguru
     :target: https://app.dependabot.com/accounts/legumeinfo/repos/236847525
     :alt: dependabot dependencies
