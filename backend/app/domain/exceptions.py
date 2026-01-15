class DomainError(Exception): pass

class UsernameTooShortError(DomainError): pass
class UserAlreadyExistsError(DomainError): pass
class UserNotFoundError(DomainError): pass
class InvalidPasswordError(DomainError): pass
class NotAuthenticatedError(DomainError): pass
class NotFound(DomainError): pass