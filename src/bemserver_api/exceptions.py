"""Exceptions"""


class BEMServerAPIError(Exception):
    """Base BEMServer API exception"""


class BEMServerAPIAuthenticationError(BEMServerAPIError):
    """AuthenticationError error"""

    def __init__(self, code):
        self.code = code
