""" All errors raised by the application should be here """

class ConfigurationError(Exception):
    """ The settings for the requested mode is not ok """
    message = "No configuaration"
    code = 500

    def __init__(self, key, mode='', code=500):
        super().__init__()
        self.message += " for key {}".format(key)
        if mode:
            self.message += " in mode {}".format(mode)
        self.code = code


class AuthenticationError(Exception):
    """ The settings for the requested mode is not ok """
    message = "Authentication failed. "
    code = 401

    def __init__(self, message):
        super().__init__()
        self.message += message


class QueryError(Exception):
    """ The settings for the requested mode is not ok """
    message = "Search failed. "
    code = 400

    def __init__(self, message):
        super().__init__()
        self.message += message
