class Config(object):
    BASE_URL = "127.0.0.1"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SECRET_KEY = "REPLACE IT"
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"
    DEFAULT_RATELIMIT = ["500/minute"]

class QAConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SECRET_KEY = "REPLACE IT"
    SQLALCHEMY_DATABASE_URI = "sqlite:///qa.db"
    DEFAULT_RATELIMIT = ["1/minute"]

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SECRET_KEY = "REPLACE IT"
    SQLALCHEMY_DATABASE_URI = "sqlite:///main.db"
    DEFAULT_RATELIMIT = ["100/minute"]
