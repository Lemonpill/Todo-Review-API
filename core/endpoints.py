import re
from flask import Blueprint, current_app, jsonify
import jwt
from datetime import datetime, timedelta
from flask.wrappers import Response
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.functions import current_date
from core.app import database as db
from pydantic.error_wrappers import ValidationError
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, Unauthorized
from werkzeug.security import check_password_hash
from .models import (
    User,
    Todo,
    Item,
    Review
)
from .schemas import (
    CredentialsShema,
    CreateTodoSchema,
    CreateItemSchema,
    CreateReviewSchema,
    UpdateTodoSchema,
    UpdateItemSchema,
    UpdateReviewSchema,
    PaginationSchema,
    BearerSchema,
    RefreshSchema,
    errors_to_response
)
from .decorators import (
    json_required,
    bearer_required,
    bearer_optional,
    pagination_required,
    refresh_required
)


### BLUEPRINTS ###
auth = Blueprint(name='auth', import_name=__name__)
users = Blueprint(name='users', import_name=__name__)
todos = Blueprint(name='todos', import_name=__name__)
reviews = Blueprint(name='reviews', import_name=__name__)


### ROUTES ###
@auth.route("register", methods=["POST"])
@json_required
def create_user(json_data):
    """
    Create a new user
    """
    try:
        parsed = CredentialsShema(**json_data)
    except ValidationError as e:
        return errors_to_response(e.errors())
    user_exists = User.get_by_username(parsed.username)
    try:
        assert not user_exists
    except AssertionError:
        raise BadRequest(description="username exists")
    User.create(parsed)
    db.session.commit()
    return Response(status=201)
    

@auth.route("token", methods=["POST"])
@json_required
def create_bearer(json_data):
    """
    Generate bearer + refresh tokens
    """
    try:
        parsed = CredentialsShema(**json_data)
    except ValidationError:
        raise Unauthorized(description="could not authorize")
    user = User.get_by_username(parsed.username)
    try:
        assert user
    except AssertionError:
        raise Unauthorized(description="could not authorize")
    try:
        assert check_password_hash(user.password, parsed.password)
    except AssertionError:
        raise Unauthorized(description="could not authorize")
    bearer = jwt.encode(
        payload={
            "uid": user.id,
            "exp": datetime.now() + timedelta(minutes=15),
            "scp": "access"
        },
        key=current_app.secret_key
    )
    refresh = jwt.encode(
        payload={
            "uid": user.id,
            "exp": datetime.now() + timedelta(hours=5),
            "scp": "refresh"
        },
        key=current_app.secret_key
    )
    return {
        "token": bearer,
        "refresh": refresh
    }, 201

@refresh_required
@auth.route("refresh", methods=["POST"])
@refresh_required
def refresh_bearer(current_user):
    """
    Generates and returns a refreshed bearer
    """
    # generate bearer token
    bearer = jwt.encode(
        payload={
            "uid": current_user.id,
            "exp": datetime.now() + timedelta(minutes=15),
            "scp": "access"
        },
        key=current_app.secret_key
    )
    # return response
    return {"token": bearer}, 201


@users.route("<username>", methods=["GET"])
@bearer_required
def get_user_info(current_user, username):
    try:
        assert current_user.username == username
    except:
        raise Forbidden(description="could not authorize")
    return current_user.get_info()

@users.route("<username>", methods=["PATCH"])
@json_required
@bearer_required
def update_user_info(current_user, json_data, username):
    try:
        assert current_user.username == username
    except:
        raise Forbidden(description="could not authorize")
    try:
        parsed = CredentialsShema(**json_data)
    except ValidationError as e:
        return errors_to_response(e.errors())
    try:
        assert not User.get_by_username(parsed.username)
    except AssertionError:
        raise BadRequest(description="username exists")
    current_user.update(parsed)
    db.session.commit()
    return Response(status=200)

@users.route("<username>", methods=["DELETE"])
@bearer_required
def delete_user(current_user, username):
    try:
        assert current_user.username == username
    except:
        raise Forbidden(description="could not authorize")
    current_user.delete()
    db.session.commit()
    return Response(status=200)


@todos.route("best", methods=["GET"])
@pagination_required
def get_top_todos(offset, limit):
    result = list()
    todos = Todo.best(offset, limit)
    for todo in todos:
        result.append(todo.get_info())
    return jsonify(result)

@todos.route("", methods=["GET"])
@pagination_required
@bearer_optional
def get_all_todos(current_user, offset, limit):
    if current_user:
        todos = Todo.get_all_public_or_by_user(current_user, offset, limit)
    else:
        todos = Todo.get_all_public(offset, limit)
    result = list()
    for todo in todos:
        result.append(todo.get_info())
    return jsonify(result)

@todos.route("<int:todo_id>", methods=["GET"])
@bearer_optional
def get_todo_info(current_user, todo_id):
    if current_user:
        todo = Todo.get_single_public_or_by_user(current_user, todo_id)
    else:
        todo = Todo.get_single_public(todo_id)
    try:
        assert todo
    except AssertionError:
        raise NotFound(description="todo not found")
    return todo.get_info()

@todos.route("", methods=["POST"])
@bearer_required
@json_required
def create_todo(json_data, current_user):
    try:
        parsed = CreateTodoSchema(**json_data)
    except ValidationError as e:
        return errors_to_response(e.errors())
    current_user.create_todo(parsed)
    db.session.commit()
    return Response(status=201)

@todos.route("<int:todo_id>", methods=["PATCH"])
@bearer_required
@json_required
def update_todo(json_data, current_user, todo_id):
    todo = current_user.get_todo_by_id(todo_id)
    try:
        assert todo
    except AssertionError:
        raise NotFound(description="todo not found")
    try:
        parsed = CreateTodoSchema(**json_data)
    except ValidationError as e:
        return errors_to_response(e.errors())
    todo.update(parsed)
    db.session.commit()
    return Response(status=200)

@todos.route("<int:todo_id>", methods=["DELETE"])
@bearer_required
def delete_todo(current_user, todo_id):
    todo = current_user.get_todo_by_id(todo_id)
    try:
        assert todo
    except AssertionError:
        raise NotFound(description="todo not found")
    todo.delete()
    db.session.commit()
    return Response(status=200)

@todos.route("<int:todo_id>/items", methods=["GET"])
@pagination_required
@bearer_optional
def get_todo_items(current_user, offset, limit, todo_id):
    if current_user:
        todo = Todo.get_single_public_or_by_user(current_user, todo_id)
    else:
        todo = Todo.get_single_public(todo_id)
    try:
        assert todo
    except AssertionError:
        raise NotFound(description="todo not found")
    items = todo.get_items(offset, limit)
    result = list()
    for item in items:
        result.append(item.get_info())
    return jsonify(result)

@todos.route("<int:todo_id>/items", methods=["POST"])
@bearer_required
@json_required
def create_todo_item(json_data, current_user, todo_id):
    todo = current_user.get_todo_by_id(todo_id)
    try:
        assert todo
    except AssertionError:
        raise NotFound(description="todo not found")
    try:
        parsed = CreateItemSchema(**json_data)
    except ValidationError as e:
        return errors_to_response(e.errors())
    try:
        assert not todo.is_full()
    except AssertionError:
        raise BadRequest(description="todo can contain up to 100 items")
    todo.add_item(parsed)
    db.session.commit()
    return Response(status=201)

@todos.route("<int:todo_id>/items/<int:item_id>", methods=["GET"])
@bearer_optional
def get_item_info(current_user, todo_id, item_id):
    """
    Fetch todo item info
    """
    if current_user:
        todo = Todo.get_single_public_or_by_user(current_user, todo_id)
    else:
        todo = Todo.get_single_public(todo_id)
    try:
        assert todo
    except AssertionError:
        raise NotFound(description="todo not found")
    item = todo.get_item_by_id(item_id)
    try:
        assert item
    except AssertionError:
        raise NotFound(description="item not found")
    return item.get_info()
    
@todos.route("<int:todo_id>/items/<int:item_id>", methods=["PATCH"])
@bearer_required
@json_required
def update_item_info(json_data, current_user, todo_id, item_id):
    todo = current_user.get_todo_by_id(todo_id)
    try:
        assert todo
    except AssertionError:
        raise NotFound(description="todo not found")
    item = todo.get_item_by_id(item_id)
    try:
        assert item
    except AssertionError:
        raise NotFound(description="item not found")
    try:
        parsed = CreateItemSchema(**json_data)
    except ValidationError as e:
        return errors_to_response(e.errors())
    item.update(parsed)
    db.session.commit()
    return Response(status=200)

@todos.route("<int:todo_id>/items/<int:item_id>", methods=["DELETE"])
@bearer_required
def delete_item(current_user, todo_id, item_id):
    todo = current_user.get_todo_by_id(todo_id)
    try:
        assert todo
    except AssertionError:
        raise NotFound(description="todo not found")
    item = todo.get_item_by_id(item_id)
    try:
        assert item
    except AssertionError:
        raise NotFound(description="item not found")
    item.delete()
    db.session.commit()
    return Response(status=200)

@todos.route("<int:todo_id>/reviews", methods=["GET"])
@pagination_required
@bearer_optional
def get_todo_reviews(current_user, offset, limit, todo_id):
    if current_user:
        todo = Todo.get_single_public_or_by_user(current_user, todo_id)
    else:
        todo = Todo.get_single_public(todo_id)
    try:
        assert todo
    except AssertionError:
        raise NotFound(description="todo not found")
    reviews = todo.reviews
    result = list()
    for review in reviews:
        result.append(review.get_info())
    return jsonify(result)

@todos.route("<int:todo_id>/reviews", methods=["POST"])
@bearer_required
@json_required
def create_todo_review(json_data, current_user, todo_id):
    todo = Todo.get_by_id(todo_id)
    try:
        assert todo.public
    except AssertionError:
        raise NotFound(description="todo must be public")
    try:
        assert todo.owner != current_user
    except AssertionError:
        raise Forbidden(description="can not review your own")
    try:
        assert not todo.get_review_by_user(current_user)
    except AssertionError:
        raise BadRequest(description="already reviewed")
    try:
        parsed = CreateReviewSchema(**json_data)
    except ValidationError as e:
        return errors_to_response(e.errors())
    todo.add_review(parsed, current_user)
    db.session.commit()
    return Response(status=201)


@reviews.route("", methods=["GET"])
@pagination_required
@bearer_optional
def get_all_reviews(current_user, offset, limit):
    if current_user:
        reviews = Review.get_all_public_or_by_user(current_user, offset, limit)
    else:
        reviews = Review.get_all_public(offset, limit)
    result = list()
    for review in reviews:
        result.append(review.get_info())
    return jsonify(result)

@reviews.route("<int:review_id>", methods=["GET"])
@bearer_optional
def get_review_info(current_user, review_id):
    if current_user:
        review = Review.get_single_public_or_by_user(review_id, current_user)
    else:
        review = Review.get_single_public(review_id)
    try:
        assert review
    except AssertionError:
        raise NotFound(description="review not found")
    return review.get_info()

@reviews.route("<int:review_id>", methods=["PATCH"])
@bearer_required
@json_required
def update_review_info(json_data, current_user, review_id):
    review = current_user.get_review_by_id(review_id)
    try:
        assert not review.todo.public
    except AssertionError:
        raise Forbidden(description="could not complete request")
    try:
        parsed = CreateReviewSchema(**json_data)
    except ValidationError as e:
        return errors_to_response(e.errors())
    review.update(parsed)
    db.session.commit()
    return Response(status=200)

@reviews.route("<int:review_id>", methods=["DELETE"])
@bearer_required
def delete_review(current_user, review_id):
    review = current_user.get_review_by_id(review_id)
    try:
        assert not review.todo.public
    except AssertionError:
        raise Forbidden(description="could not complete request")
    review.delete()
    db.session.commit()
    return Response(status=200)
