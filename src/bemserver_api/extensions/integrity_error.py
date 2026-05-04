"""Integrity error management

Catch integrity errors in resources and return appropriate error code.
"""

import contextlib

import psycopg.errors as ppe
import sqlalchemy as sqla

from flask_smorest import abort

from bemserver_core.exceptions import BEMServerCoreIntegrityError


class catch_integrity_error(contextlib.ContextDecorator):
    """Context manager catching integrity errors

    Can be used as context manager or decorator.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type and issubclass(exc_type, BEMServerCoreIntegrityError):
            abort(409, message=str(exc_value))
        if exc_type and issubclass(exc_type, sqla.exc.IntegrityError):
            if isinstance(exc_value.orig, ppe.UniqueViolation):
                abort(409, message="Unique constraint violation")
            if isinstance(exc_value.orig, ppe.ForeignKeyViolation):
                abort(409, message="Foreign key constraint violation")
            # Shouldn't happen
            abort(409)
        return False
