class SnBaseException(Exception):
    pass


class NotValidDataError(SnBaseException):
    def __init__(self, message, field_name: str):
        messages = (
            [message] if isinstance(message, (str, bytes)) else message
        )
        self.messages = {field_name: messages}
        super().__init__(message)
