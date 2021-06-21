from functools import wraps
from flask import request, json
from marshmallow import ValidationError
from app.helper import format_error


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        pass

def param_required(schema):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                schema.load(request.form)
            except ValidationError as err:
                return json.jsonify(format_error(err.messages)), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator
