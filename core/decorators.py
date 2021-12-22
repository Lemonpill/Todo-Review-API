from flask import request, current_app
from functools import wraps
import jwt
from jwt.exceptions import PyJWTError
from pydantic.error_wrappers import ValidationError
from werkzeug.exceptions import (
    BadRequest,
    Unauthorized
)
from .schemas import (
    PaginationSchema,
    errors_to_response,
    BearerSchema
)
from .models import User


def decorator_boilerplate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = None
        return f(data, *args, **kwargs)
    return decorated

def json_required(f):
    """
    Verifies request contains a valid json
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        data = None
        try:
            assert request.is_json
        except AssertionError:
            raise BadRequest(description="content-type must be application/json")
        try:
            data = request.get_json()
        except Exception:
            raise BadRequest(description="invalid json format")
        try:
            assert isinstance(data, dict)
        except AssertionError:
            raise BadRequest(description="invalid json format")
        return f(data, *args, **kwargs)
    return decorated

def bearer_required(f) -> User:
    """
    1. Verifies request header contains authorization token (type 'access')
    2. Decodes the bearer and returns the relevant user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            assert "Authorization" in request.headers
        except AssertionError:
            raise Unauthorized(description="could not authenticate")
        auth_header = {
            "Authorization": request.headers["Authorization"]
        }
        try:
            token = BearerSchema(**auth_header)
        except ValidationError:
            raise Unauthorized(description="could not authenticate")
        try:
            decoded = jwt.decode(
                jwt=token.Authorization[7:],
                key=current_app.secret_key,
                algorithms=["HS256"]
            )
        except PyJWTError:
            raise Unauthorized(description="could not authenticate")
        try:
            assert decoded["scp"] == "access"
        except AssertionError:
            raise Unauthorized(description="could not authenticate")
        user = User.get_by_id(decoded["uid"])
        if not user:
            raise Unauthorized(description="could not authenticate")
        
        return f(user, *args, **kwargs)
    return decorated

def bearer_optional(f) -> User|None:
    """
    1. In case no authorization was provided, returns None
    2. Verifies request header contains authorization token (scope 'access')
    3. Decodes the bearer and returns the relevant user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # no authorization
        if "Authorization" not in request.headers:
            return f(None, *args, **kwargs)
        # bearer authorization 
        auth_header = {
            "Authorization": request.headers["Authorization"]
        }
        try:
            token = BearerSchema(**auth_header)
        except ValidationError:
            raise Unauthorized(description="could not authenticate")
        try:
            decoded = jwt.decode(
                jwt=token.Authorization[7:],
                key=current_app.secret_key,
                algorithms=["HS256"]
            )
        except PyJWTError:
            raise Unauthorized(description="could not authenticate")
        try:
            assert decoded["scp"] == "access"
        except AssertionError:
            raise Unauthorized(description="could not authenticate")
        user = User.get_by_id(decoded["uid"])
        if not user:
            raise Unauthorized(description="could not authenticate")
        return f(user, *args, **kwargs)
    return decorated

def refresh_required(f):
    """
    1. Verifies request header contains authorization token (scope 'refresh')
    2. Decodes the bearer and returns the relevant user
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> User:
        try:
            assert "Authorization" in request.headers
        except AssertionError:
            raise Unauthorized(description="could not authenticate")
        auth_header = {
            "Authorization": request.headers["Authorization"]
        }
        try:
            token = BearerSchema(**auth_header)
        except ValidationError:
            raise Unauthorized(description="could not authenticate")
        try:
            decoded = jwt.decode(
                jwt=token.Authorization[7:],
                key=current_app.secret_key,
                algorithms=["HS256"]
            )
        except PyJWTError:
            raise Unauthorized(description="could not authenticate")
        try:
            assert decoded["scp"] == "refresh"
        except AssertionError:
            raise Unauthorized(description="could not authenticate")
        user = User.get_by_id(decoded["uid"])
        if not user:
            raise Unauthorized(description="could not authenticate")
        return f(user, *args, **kwargs)
    return decorated

def pagination_required(f):
    """ 
    Verifies request params contain a valid offset and a limit
    In case those are missing, offset defaults to 0 and limit defaults to 100
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        if not offset:
            offset = 0
        if not limit:
            limit = 100
        try:
            data = PaginationSchema(**{
                "offset": offset,
                "limit": limit
            })
        except ValidationError as e:
            return errors_to_response(e.errors())
        return f(data.offset, data.limit, *args, **kwargs)
    return decorated