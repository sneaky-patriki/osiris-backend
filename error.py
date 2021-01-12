from werkzeug.exceptions import HTTPException

class InputError(HTTPException):
    code = 400
    message = 'No message specified'

class AccessError(HTTPException):
    code = 400
    message = 'No message specified'

class DependencyError(HTTPException):
    code = 400
    message = 'No message specified'
