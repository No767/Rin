class Error(Exception):
    pass


class UnknownPlayer(Error):
    pass


class NotFoundHTTPException(Error):
    pass


class NoItemsError(Error):
    pass