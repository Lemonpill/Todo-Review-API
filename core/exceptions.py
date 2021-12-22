from flask import json
from flask.wrappers import Response
from werkzeug.exceptions import HTTPException
from core.app import error_log

def exceptions_handler(e):
    """ Exceptions handler """
    if isinstance(e, HTTPException):
        msg = e.description
        return {"message": msg}, e.code
    else:
        msg = "internal error"
        error_log.write(e)
        return {"message": "internal error"}, 500