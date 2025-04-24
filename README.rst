snake.mcp.server
================

.. image:: https://codecov.io/gh/yourusername/snake-mcp-server/branch/main/graph/badge.svg
  :target: https://codecov.io/gh/yourusername/snake-mcp-server

Python development tools for the Model Context Protocol (MCP) server.

Overview
--------

This package provides a set of tools for Python development through the MCP server interface. 
It currently includes support for running common development tasks like testing, linting,
and type checking.

Tools
-----

- **pytest**: Run pytest on a Python project with coverage reporting
- **mypy**: Run mypy type checking on a Python project
- **flake8**: Run flake8 linter on a Python project

All tools provide structured output with detailed information about test results, type issues,
and linting problems.

Installation
-----------

.. code-block:: bash

    pip install -e .

Usage
-----

Import and use the tools:

.. code-block:: python

    from snake.mcp.server.server import pytest, mypy, flake8

    # Run pytest with coverage
    result = await pytest(
        ctx, 
        path="/path/to/python/project", 
        verbose=True,
        coverage=True,
        coverage_source="mypackage"
    )

    # Run mypy type checking
    result = await mypy(
        ctx, 
        path="/path/to/python/project",
        disallow_untyped_defs=True
    )

    # Run flake8 linting
    result = await flake8(
        ctx, 
        path="/path/to/python/project", 
        max_line_length=88
    )

Architecture
-----------

- **Server Interface**: Defined in `server.py` with tools exposed as MCP-compatible functions
- **Tool Implementations**: Located in the `tools/` directory
  - Each tool has its own implementation module
  - `coverage.py` provides coverage parsing utilities
- **Error Handling**: Centralized in `server.py` with specific exceptions raised in tool modules

Development
----------

- Test coverage: 99%
- Code style: Enforced with flake8
- Type checking: Validated with mypy

To run tests:

.. code-block:: bash

    pytest
    
With coverage:

.. code-block:: bash

    pytest --cov=snake

Code Coverage Requirements
------------------------

We maintain a minimum code coverage requirement of 95.0%. This threshold is defined in the `pytest.ini` file in the repository root.

When running pytest, the coverage check is automatically performed:

.. code-block:: bash

    pytest

If code coverage drops below the 95% threshold, tests will automatically fail with an error message like:

.. code-block:: text

    FAIL Required test coverage of 95% not reached. Total coverage: 94.2%

If this happens, you'll need to add more tests to increase coverage before your changes can be accepted.
