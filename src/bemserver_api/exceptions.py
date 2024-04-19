"""Exceptions"""


class BEMServerAPIError(Exception):
    """Base BEMServer API exception"""


class BEMServerAPIAuthenticationError(BEMServerAPIError):
    """AuthenticationError error"""
