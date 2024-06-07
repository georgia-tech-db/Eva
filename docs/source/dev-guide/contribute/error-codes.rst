Using Error Codes in EvaDB
==========================

Introduction
------------

Proper error handling is an essential aspect of robust software development. In EvaDB, error codes provide a standardized way of reporting and logging errors. This guide explains how to use predefined error codes, and how they enhance debugging and error tracking.

Error Codes Overview
--------------------

EvaDB implements an `ErrorManager` class with predefined error codes for various error scenarios. Each error code is associated with a default error message, which can be extended with additional information when required. A list of all error codes can be found in `evadb/error_manager.py`.

Using Error Codes without Additional Message
--------------------------------------------

In cases where the default error message suffices, you can use the error code directly. This is common in scenarios where the error context is self-explanatory.

.. code-block:: python

    from error_manager import ErrorManager

    # Example of using an error code without an additional message
    def some_function():
        if not some_condition:
            raise Exception(ErrorManager.get_error_message(ErrorManager.EXPECTED_SELECTION_STATEMENT))

Using Error Codes with Additional Message
-----------------------------------------

In scenarios requiring more detailed error information, you can provide an additional message along with the error code. This is useful for adding context or specifics about the error.

.. code-block:: python

    from error_manager import ErrorManager

    # Example of using an error code with an additional message
    def some_function(param):
        if not validate(param):
            error_msg = ErrorManager.get_error_message(ErrorManager.UNSUPPORTED_TYPE, f"Invalid parameter: {param}")
            raise Exception(error_msg)