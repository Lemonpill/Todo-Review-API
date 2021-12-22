from core.app import create_app
from config import Config as c

app = create_app(c)

if __name__=="__main__":
    """
    Run the Flask app
    """
    app.run(host='127.0.0.1', debug=True)
