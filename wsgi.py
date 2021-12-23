from core.app import create_app
from config import QAConfig as c

app = create_app(c)

if __name__=="__main__":
    """
    Run the Flask app
    """
    app.run(host=c.BASE_URL)
