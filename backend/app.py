from flask import Flask, render_template
from flasgger import Swagger
from .api.auth import auth_bp
from .api.routes import api_bp
from .db_repository.database import init_db

app = Flask(__name__, 
            static_folder='../frontend/public',
            template_folder='../frontend/src/templates')

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger = Swagger(app, config=swagger_config)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 