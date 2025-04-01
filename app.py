from flask import Flask
from routes import routes_bp  # Import the Blueprint
from config import get_db_connection

app = Flask(__name__)

# Register the Blueprint
app.register_blueprint(routes_bp)

if __name__ == "__main__":
    app.run(debug=True)
