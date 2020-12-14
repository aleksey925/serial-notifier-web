from common.exceptions import SerialNotifierBaseException


class LoginException(SerialNotifierBaseException):
    pass


class CredentialsNotValid(LoginException):
    pass


class UserAlreadyExists(SerialNotifierBaseException):
    def __init__(self, not_unique_field):
        self.not_unique_field = not_unique_field
