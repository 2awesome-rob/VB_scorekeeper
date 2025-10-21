from flask import Flask
from reactpy.backend.flask import configure
from app.routes import register_routes, App

def create_app():
    app = Flask(__name__)
    
    # Register routes
    register_routes(app)
    
    # Configure ReactPy with Flask
    configure(app, App)
    
    return app