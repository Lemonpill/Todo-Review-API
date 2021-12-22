from datetime import datetime
from core.app import database as db
from core.models import User, Todo, Item, Review
import random, string

def username_generator(n):
    return ''.join(
        random.choices(
            string.ascii_lowercase + string.digits, k=n
        )
    )

def password_generator(n):
    return ''.join(
        random.choices(
            string.ascii_lowercase + string.digits + string.punctuation, k=n
        )
    )


def create_users(n=100):
    i = 0
    while i < n:
        print(f'create user (iteration #{i})')
        user = User(
            username=username_generator(10),
            password=password_generator(10),
            created=datetime.now()
        )
        db.session.add(user)
        i += 1
    db.session.commit()

def create_todos(users, n=100):
    for user in users:
        i = 0
        while i < n:
            todo = Todo(
                user_id=user.id,
                title=f"todo #{i} for user #{user.id}",
                public=random.randrange(0, 2),
                created=datetime.now()
            )
            user.todos.append(todo)
            i += 1
    db.session.commit()

def create_items(todos, n=100):
    for t in todos:
        i = 0
        while i < n:
            item = Item(
                todo_id=t.id,
                content=f"todo #{t.id} item #{i}",
                completed=random.randrange(0, 2),
                created=datetime.now()
            )
            t.items.append(item)
            i += 1
    db.session.commit()

def create_reviews(users, todos):
    for user in users:
        for todo in todos:
            if todo not in user.todos:
                review = Review(
                    user_id=user.id,
                    todo_id=todo.id,
                    title=f"todo #{todo.id} review",
                    content=f"todo #{todo.id} review by user {user.id}",
                    stars=random.randrange(1, 6),
                    created=datetime.now()
                )
                todo.reviews.append(review)
    db.session.commit()

def populate_db():
    create_users(1000)
    users = db.session.query(User).all()
    create_todos(users, n=100)
    todos = db.session.query(Todo).all()
    create_items(todos, n=100)
    create_reviews(users, todos)

if __name__=="__main__":
    populate_db()
