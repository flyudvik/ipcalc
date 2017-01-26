class IPCalcBaseException(Exception):
    pass


class WrongNumberOfHosts(IPCalcBaseException):
    pass


class ValidationError(IPCalcBaseException):
    pass


class WrongNetworkException(IPCalcBaseException):
    pass
