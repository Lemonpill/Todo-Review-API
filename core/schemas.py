### CONSTANTS ###
USERNAME_MINLEN = 1
USERNAME_MAXLEN = 50
USERNAME_REGEX = r'^\w+$'

PASS_MINLEN = 8
PASS_MAXLEN = 2048
PASS_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&]).*$"

BEARER_MINLEN = 143
BEARER_MAXLEN = 160

REFRESH_MINLEN = 144
REFRESH_MAXLEN = 160

TOKEN_REGEX = r"^(Bearer [\w-]*\.[\w-]*\.[\w-]*$)"

TODO_TITLE_MINLEN = 1
TODO_TITLE_MAXLEN = 50

ITEM_CONTENT_MINLEN = 1
ITEM_CONTENT_MAXLEN = 50

REVIEW_TITLE_MINLEN = 1
REVIEW_TITLE_MAXLEN = 50

REVIEW_CONTENT_MINLEN = 1
REVIEW_CONTENT_MAXLEN = 5000

MIN_OFFSET = 0
MAX_OFFSET = 999999999

MIN_LIMIT = 1
MAX_LIMIT = 100


# FUNCTIONS #
def errors_to_dict(errs):
    """
    Generate dictionary from pydantic errors
    """
    errors = dict()
    for e in errs:
        errors[e["loc"][0]] = e["msg"]
    return errors

def errors_to_response(errors):
    """
    Generate response from pydantic errors
    """
    return {
        "message": "validation error",
        "errors": errors_to_dict(errors)
    }, 400, {
        "X-Validation-Error": "Validation error"
    }


# SCHEMAS #
from enum import IntEnum
from pydantic import BaseModel, Field


class ReviewStarsEnum(IntEnum):
    one=1
    two=2
    three=3
    four=4
    five=5

class CredentialsShema(BaseModel):
    """
    Parsing and validating requests that include user credentials
    """
    username: str = Field(
        ..., # is required
        min_length=USERNAME_MINLEN,
        max_length=USERNAME_MAXLEN,
        regex=USERNAME_REGEX
        )
    password: str = Field(
        ..., # is required
        min_length=PASS_MINLEN,
        max_length=PASS_MAXLEN,
        regex=PASS_REGEX
        )

class BearerSchema(BaseModel):
    """
    Parse requests involving Bearer
    """
    Authorization: str = Field(
        ..., # is required
        min_length=BEARER_MINLEN,
        max_length=BEARER_MAXLEN,
        regex=TOKEN_REGEX
        )

class RefreshSchema(BaseModel):
    """
    Parse requests involving Refresh token
    """
    Authorization: str = Field(
        ..., # is required
        min_length=REFRESH_MINLEN,
        max_length=REFRESH_MAXLEN,
        regex=TOKEN_REGEX
        )

class CreateItemSchema(BaseModel):
    """
    Parse requests that create Todo items
    """
    content: str = Field(
        ..., # is required
        min_length=ITEM_CONTENT_MINLEN,
        max_length=ITEM_CONTENT_MAXLEN
        )
    completed: bool = Field(...) # is required

class UpdateItemSchema(BaseModel):
    """
    Parse requests that update Todo items
    """
    content: str = Field(
        ..., # is required
        min_length=ITEM_CONTENT_MINLEN,
        max_length=ITEM_CONTENT_MAXLEN
        )
    completed: bool = Field(...) # is required

class CreateTodoSchema(BaseModel):
    """
    Parse requests that create Todos
    """
    title: str = Field(
        ..., # is required
        min_length=TODO_TITLE_MINLEN,
        max_length=TODO_TITLE_MAXLEN
        )
    public: bool = Field(...) # is required

class UpdateTodoSchema(BaseModel):
    """
    Parse requests that update Todos
    """
    title: str = Field(
        ..., # is required
        min_length=TODO_TITLE_MINLEN,
        max_length=TODO_TITLE_MAXLEN
        )
    private: bool = Field(...) # is required

class CreateReviewSchema(BaseModel):
    """
    Parse requests that create Reviews
    """
    stars: ReviewStarsEnum = Field(...) # is required
    title: str = Field(
        ..., # is required
        min_length=REVIEW_TITLE_MINLEN,
        max_length=REVIEW_TITLE_MAXLEN
        )
    content: str = Field(
        ..., # is required
        min_length=REVIEW_CONTENT_MINLEN,
        max_length=REVIEW_CONTENT_MAXLEN
        )

class UpdateReviewSchema(BaseModel):
    """
    Parse requests that update Reviews
    """
    stars: ReviewStarsEnum = Field(...) # is required
    title: str = Field(
        ..., # is required
        min_length=REVIEW_TITLE_MINLEN,
        max_length=REVIEW_TITLE_MAXLEN
        )
    content: str = Field(
        ..., # is required
        min_length=REVIEW_CONTENT_MINLEN,
        max_length=REVIEW_CONTENT_MAXLEN
        )

class PaginationSchema(BaseModel):
    """
    Parse requests that require pagination
    """
    offset: int = Field(
        ..., # is required
        ge=MIN_OFFSET,
        le=MAX_OFFSET,
        )
    limit: int = Field(
        ..., # is required
        ge=MIN_LIMIT,
        le=MAX_LIMIT
        )