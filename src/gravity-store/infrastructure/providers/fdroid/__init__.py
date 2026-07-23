"""Integração com os endpoints públicos do F-Droid."""

from .client import FdroidApiError, FdroidClient, FdroidInputError, FdroidNotFoundError

__all__ = ["FdroidApiError", "FdroidClient", "FdroidInputError", "FdroidNotFoundError"]
