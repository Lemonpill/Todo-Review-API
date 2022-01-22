import requests, random, string, json

global bearer, refresh

def log(file, text):
    with open(file, "a") as f:
        f.write(f"{text}\n")

def string_gen(n):
    return ''.join(
        random.choices(
            string.ascii_lowercase + string.digits, k=n
        )
    )

class User:
    def __init__(self, username, password) -> None:
        self.id = None
        self.username = username
        self.password = password
        self.bearer = None
        self.refresh = None
        self.item = list()
        self.reviews = list()

class Todo:
    def __init__(self, id, user_id, public) -> None:
        self.id = id
        self.user_id = user_id
        self.public = public

server_url = "http://127.0.0.1:5000/"
log_file = "testing.log"
user_password = "NewPass0123!@#$"
test_users = list()
test_todos = list()

def test_create_users(n=100):
    i = 0
    while i < n:
        test_users.append(
            User(
                username=string_gen(20),
                password="NewPass0123!@#$"
            )
        )
        i += 1
    for u in test_users:
        response = requests.post(
            url=server_url + "auth/register",
            headers={
                "content-type": "application/json"
            },
            data=json.dumps(
                {
                    "username": u.username,
                    "password": u.password
                }
            )
        )
        assert response.status_code == 201, response.json()
        response_data = response.json()
        u.id = response_data["id"]
        log(log_file, f"{response_data}")

def test_authenticate_users():
    for u in test_users:
        response = requests.post(
            url=server_url + "auth/token",
            headers={
                "content-type": "application/json"
            },
            data=json.dumps(
                {
                    "username": u.username,
                    "password": u.password
                }
            )
        )
        assert response.status_code == 201, response.json()
        response_data = response.json()
        u.bearer = response_data["token"]
        u.refresh  = response_data["refresh"]
        log(log_file, f"{response_data}")

def test_create_todos(n=100):
    for u in test_users:
        i = 0
        while i < n:
            response = requests.post(
                url=server_url + "todos",
                headers={
                    "content-type": "application/json",
                    "Authorization": f"Bearer {u.bearer}"
                },
                data=json.dumps(
                    {
                        "title": f"new todo",
                        "public": random.randrange(2)
                    }
                )
            )
            assert response.status_code == 201
            response_data = response.json()
            todo = Todo(
                id=response_data["id"],
                user_id=response_data["user_id"],
                public=response_data["public"]
            )
            test_todos.append(todo)
            log(log_file, f"{response_data}")
            i += 1

def test_create_items(n=3):
    for user in test_users:
        for todo in test_todos:
            if todo.user_id == user.id:
                i = 0
                while i < n:
                    response = requests.post(
                        url=server_url + f"todos/{todo.id}/items",
                        headers={
                            "content-type": "application/json",
                            "Authorization": f"Bearer {user.bearer}"
                        },
                        data=json.dumps(
                            {
                                "content": f"new todo item",
                                "completed": random.randrange(2)
                            }
                        )
                    )
                    assert response.status_code == 201, response.json()
                    response_data = response.json()
                    log(log_file, f"{response_data}")
                    i += 1

def test_create_reviews():
    for user in test_users:
        for todo in test_todos:
            if todo.user_id != user.id \
                and todo.public:
                response = requests.post(
                    url=server_url + f"todos/{todo.id}/reviews",
                    headers={
                        "content-type": "application/json",
                        "Authorization": f"Bearer {user.bearer}"
                    },
                    data=json.dumps(
                        {
                            "title": "new todo review",
                            "content": "new todo review content",
                            "stars": random.randrange(1, 6)
                        }
                    )
                )
                assert response.status_code == 201, response.json()
                response_data = response.json()
                log(log_file, f"{response_data}")
