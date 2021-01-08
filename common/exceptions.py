class SerialNotifierBaseException(Exception):
    pass


class DataBaseException(SerialNotifierBaseException):
    pass


class ObjectDoesNotExist(DataBaseException):
    pass
