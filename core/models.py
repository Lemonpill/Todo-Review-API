from datetime import datetime
from sqlalchemy.sql.expression import and_, or_
from core.app import database as db
from sqlalchemy_utils import aggregated
from werkzeug.security import generate_password_hash
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    Boolean,
    DateTime,
    Float,
    func
)


### MODELS ###
class User(db.Model):
    """ ORM for 'user' table """

    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(100))
    created = Column(DateTime, default=None)
    updated = Column(DateTime, default=None)

    todos = db.relationship("Todo", backref="owner", lazy="dynamic")
    reviews = db.relationship("Review", backref="owner", lazy="dynamic")
    
    @staticmethod
    def create(data):
        """
        Create a new user
        """

        user = User(
            username=data.username,
            password=generate_password_hash(data.password, "SHA256"),
            created=datetime.now()
        )
        db.session.add(user)
    
    @staticmethod
    def get_all(offset=0, limit=100):
        """
        Fetch all users
        """

        return db.session.query(User).offset(offset).limit(limit)

    @staticmethod
    def get_by_id(user_id):
        """
        Fetch user by ID
        """

        return db.session.query(User).filter_by(id=user_id).first()

    @staticmethod
    def get_by_username(username):
        """
        Fetch user by username
        """

        return db.session.query(User).filter_by(username=username).first()

    def to_dict(self):
        """
        Get instance dictionary
        """

        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "created": self.created,
            "updated": self.updated
        }

    def get_info(self):
        """
        Get entry info
        """

        return {
            "id": self.id,
            "username": self.username,
            "created": self.created,
            "updated": self.updated
        }

    def update(self, data):
        """
        Update current entry
        """
        
        self.username = data.username
        self.password = generate_password_hash(data.password, "SHA256")
        self.updated = datetime.now()

    def create_todo(self, data):
        """
        Create a new todo
        """
        todo = Todo(
            user_id=self.id,
            title=data.title,
            public=data.public,
            created=datetime.now()
        )
        self.todos.append(todo)

    def get_todo_by_id(self, todo_id):
        """
        Fetch user todo by id
        """

        return self.todos.filter_by(id=todo_id).first()

    def get_todos(self, offset=0, limit=100):
        """
        Fetch all user todos
        """

        return self.todos.offset(offset).limit(limit)

    def get_private_todos(self, offset=0, limit=100):
        """
        Fetch user private todos
        """

        return self.todos.filter_by(public=False).offset(offset).limit(limit)

    def get_public_todos(self, offset=0, limit=100):
        """
        Fetch user public todos
        """

        return self.todos.filter_by(public=True).offset(offset).limit(limit)

    def get_reviews(self, offset=0, limit=100):
        """
        Fetch user reviews
        """

        return self.reviews.offset(offset).limit(limit)

    def get_review_by_id(self, review_id):
        """
        Fetch user review by id
        """

        return self.reviews.filter_by(id=review_id).first()

    def get_review_by_todo(self, todo):
        """
        Fetch user review by todo
        """

        return self.reviews.filter(Review.todo_id==todo.id).first()

    def get_single_public_review(self, review_id):
        """
        Fetch user owned review if it belongs to a public todo
        """

        return self.reviews.join(
            Review.todo, aliased=True
        ).filter(
            Review.id == review_id,
            Todo.public == True
        ).first()

    def delete_todos(self):
        """
        Delete all user todos
        """
        
        self.todos.delete()

    def delete_reviews(self):
        """
        Delete all user reviews
        """

        self.reviews.delete()

    def delete(self):
        """
        Delete user with all todos and reviews
        """
        
        self.delete_todos()
        self.delete_reviews()
        db.session.delete(self)


class Todo(db.Model):
    """ ORM for 'todo' table """

    __tablename__ = "todo"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    title = Column(String(50))
    public = Column(Boolean, default=False)
    created = Column(DateTime, default=None)
    updated = Column(DateTime, default=None)

    items = db.relationship("Item", backref="todo", lazy="dynamic")
    reviews = db.relationship("Review", backref="todo", lazy="dynamic")

    @aggregated('reviews', Column(Float, default=0))
    def avg_stars(self):
        """
        Returns average stars for the current instance
        """

        return func.avg(Review.stars)

    @staticmethod
    def best(offset=0, limit=100):
        """
        Fetches the list of best todos sorted by rating desc
        """
        
        todos = db.session.query(Todo).filter_by(
            public=True
        ).order_by(
            Todo.avg_stars.desc()
        ).offset(offset).limit(limit)
        return todos

    @staticmethod
    def get_all_public_or_by_user(user, offset, limit):
        """
        Fetches all created by user or public todos
        """
        
        return db.session.query(Todo).filter(
            or_(
                Todo.public,
                Todo.owner == user
            )
        ).offset(offset).limit(limit)

    @staticmethod
    def get_single_public_or_by_user(user, todo_id):
        """
        Fetches single created by user or public todo
        """

        return db.session.query(Todo).filter(
            Todo.id == todo_id,
            or_(
                Todo.public,
                Todo.owner == user
            )
        ).first()

    @staticmethod
    def get_single_public(todo_id):
        """
        Fetches a single public todo by ID
        """

        return db.session.query(Todo).filter(
            Todo.id == todo_id,
            Todo.public == True
        ).first()

    @staticmethod
    def create(user, data):
        """
        Create a new todo
        """

        todo = Todo(
            user_id=user.id,
            title=data.title,
            public=data.public,
            created=datetime.now()
        )
        db.session.add(todo)
    
    @staticmethod
    def get_all(offset=0, limit=100):
        """
        Fetch all todos
        """

        return db.session.query(Todo).offset(offset).limit(limit)

    @staticmethod
    def get_all_public(offset=0, limit=100):
        """
        Fetch all public todos
        """

        return db.session.query(Todo).filter_by(public=True).offset(offset).limit(limit)

    @staticmethod
    def get_all_private(offset=0, limit=100):
        """
        Fetch all private todos
        """

        return db.session.query(Todo).filter_by(public=False).offset(offset).limit(limit)

    @staticmethod
    def get_by_id(todo_id):
        """
        Fetch todo by ID
        """

        return db.session.query(Todo).filter_by(id=todo_id).first()

    def to_dict(self):
        """
        Get instance dictionary
        """

        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "public": self.public,
            "created": self.created,
            "updated": self.updated
        }

    def get_info(self):
        """
        Get entry info
        """

        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "public": self.public,
            "created": self.created,
            "updated": self.updated,
            "avg_rating": self.avg_stars,
            "votes": self.reviews.count()
        }

    def is_full(self):
        """
        Returns True if todo contains 100+ items,
        otherwise returns false
        """
        
        return self.items.count() >= 100

    def update(self, data):
        """
        Update current entry
        """

        self.title = data.title
        self.public = data.public
        self.updated = datetime.now()

    def get_items(self, offset=0, limit=100):
        """
        Fetch todo items
        """

        return self.items.offset(offset).limit(limit)

    def get_item_by_id(self, item_id):
        """
        Fetch item by ID
        """

        return self.items.filter_by(id=item_id).first()

    def add_item(self, data):
        """
        Add item
        """
        
        item = Item(
            todo_id=self.id,
            content=data.content,
            completed=data.completed,
            created=datetime.now()
        )
        db.session.add(item)

    def add_review(self, data, user):
        """
        Create a new todo review
        """
        Review.create(self, user, data)

    def get_reviews(self, offset=0, limit=100):
        """
        Fetch todo reviews
        """

        return self.reviews.offset(offset).limit(limit)

    def get_review_by_user(self, user):
        """
        Fetch reviews by a specific user
        """

        return self.reviews.filter(Review.user_id==user.id).first()
    
    def delete_items(self):
        """
        Delete todo items
        """

        self.items.delete()

    def delete_reviews(self):
        """
        Delete todo reviews
        """
        
        self.reviews.delete()

    def delete(self):
        """
        Delete todo with all items and reviews
        """
        
        self.delete_items()
        self.delete_reviews()
        db.session.delete(self)


class Item(db.Model):
    """ ORM for 'item' table """

    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    todo_id = Column(Integer, ForeignKey("todo.id"))
    content = Column(String(50))
    completed = Column(Boolean, default=False)
    created = Column(DateTime, default=None)
    updated = Column(DateTime, default=None)

    @staticmethod
    def create(todo, data):
        """
        Create a new todo item
        """
        
        item = Item(
            todo_id=todo.id,
            content=data.content,
            completed=data.completed,
            created=datetime.now()
        )
        todo.items.append(item)
    
    @staticmethod
    def get_all(offset=0, limit=100):
        """
        Fetch all items
        """

        return db.session.query(Item).offset(offset).limit(limit)

    @staticmethod
    def get_by_id(item_id):
        """
        Fetch item by ID
        """

        return db.session.query(Item).filter_by(id=item_id).first()

    def to_dict(self):
        """
        Get instance dictionary
        """

        return {
            "id": self.id,
            "todo_id": self.todo_id,
            "content": self.content,
            "completed": self.completed,
            "created": self.created,
            "updated": self.updated
        }

    def get_info(self):
        """
        Get entry info
        """

        return {
            "id": self.id,
            "todo_id": self.todo_id,
            "content": self.content,
            "completed": self.completed,
            "created": self.created,
            "updated": self.updated
        }

    def update(self, data):
        """
        Update current entry
        """

        self.content = data.content
        self.completed = data.completed
        self.updated = datetime.now()

    def delete(self):
        """
        Delete current instance
        """
        
        db.session.delete(self)


class Review(db.Model):
    """ ORM for 'review' table """

    __tablename__ = "review"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    todo_id = Column(Integer, ForeignKey("todo.id"))
    title = Column(String(50))
    content = Column(String(5000))
    stars = Column(Integer)
    created = Column(DateTime, default=None)
    updated = Column(DateTime, default=None)


    @staticmethod
    def get_all(offset=0, limit=100):
        """
        Fetch all reviews
        """

        return db.session.query(Review).offset(offset).limit(limit)

    @staticmethod
    def get_by_id(review_id):
        """
        Fetch review by ID
        """

        return db.session.query(Review).filter_by(id=review_id).first()

    @staticmethod
    def get_all_public(offset, limit):
        """
        Fetch all reviews belonging to public todos
        """

        return Review.query.join(
            Review.todo, aliased=True
        ).filter(
            Todo.public == True
        ).offset(offset).limit(limit)

    @staticmethod
    def get_all_public_or_by_user(user, offset, limit):
        """
        Fetch all reviews belonging to public todos
        or todos that are owned by user
        """

        return Review.query.join(
            Review.todo, aliased=True
        ).filter(
            or_(
                Todo.public == True,
                Todo.owner == user
            )
        ).offset(offset).limit(limit)

    @staticmethod
    def get_single_public(review_id):
        """
        Fetch single review belonging to public todo 
        """

        return Review.query.join(
            Review.todo, aliased=True
        ).filter(
            Review.id == review_id,
            Todo.public == True
        ).first()

    @staticmethod
    def get_single_public_or_by_user(review_id, user):
        """
        Fetch single review belonging to public todo 
        """

        return Review.query.join(
            Review.todo, aliased=True
        ).filter(
            and_(
                Review.id == review_id,
                or_(
                    Todo.public == True,
                    Todo.owner == user
                )
            )
        ).first()

    def to_dict(self):
        """
        Get instance dictionary
        """

        return {
            "id": self.id,
            "user_id": self.user_id,
            "todo_id": self.todo_id,
            "title": self.title,
            "content": self.content,
            "stars": self.stars,
            "created": self.created,
            "updated": self.updated
        }

    def create(todo, user, data):
        """
        Create a review
        """
        
        review = Review(
            user_id=user.id,
            todo_id=todo.id,
            title=data.title,
            content=data.content,
            stars=data.stars,
            created=datetime.now()
        )
        todo.reviews.append(review)
        user.reviews.append(review)

    def get_info(self):
        """
        Get entry info
        """

        return {
            "id": self.id,
            "user_id": self.user_id,
            "todo_id": self.todo_id,
            "title": self.title,
            "content": self.content,
            "stars": self.stars,
            "created": self.created,
            "updated": self.updated
        }

    def update(self, data):
        """
        Update current entry
        """

        self.title = data.title
        self.content = data.content
        self.stars = data.stars
        self.updated = datetime.now()

    def delete(self):
        """
        Delete current instance
        """

        db.session.delete(self)
