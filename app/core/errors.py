class AppDomainError(Exception):
    pass


class EmailAlreadyRegisteredError(AppDomainError):
    pass


class UnauthorizedError(AppDomainError):
    pass


class NotFoundError(AppDomainError):
    pass
