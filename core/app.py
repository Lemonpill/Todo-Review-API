from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from core.logger import Log


database = SQLAlchemy()
migrate = Migrate()
error_log = Log("error.log")
limiter = Limiter(key_func=get_remote_address)


def create_app(c) -> Flask:
    """
    Create Flask app
    """
    from .exceptions import exceptions_handler

    app = Flask(__name__)
    app.config.from_object(c)
    database.init_app(app)
    migrate.init_app(app, database)
    limiter.init_app(app)
    
    from .endpoints import auth
    from .endpoints import users
    from .endpoints import todos
    from .endpoints import reviews

    app.register_error_handler(Exception, exceptions_handler)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(users, url_prefix='/users')
    app.register_blueprint(todos, url_prefix='/todos')
    app.register_blueprint(reviews, url_prefix='/reviews')

    limiter.limit(c.DEFAULT_RATELIMIT)(auth)
    limiter.limit(c.DEFAULT_RATELIMIT)(users)
    limiter.limit(c.DEFAULT_RATELIMIT)(todos)
    limiter.limit(c.DEFAULT_RATELIMIT)(reviews)

    return app